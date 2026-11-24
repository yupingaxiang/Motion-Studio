# Author: Codex | Created: 2026-11-24 20:20:10 +08:00 | Offline narration transcription and storyboard alignment.
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from threading import Lock

from pydantic import RootModel

from ..models import atomic_write_json, now_iso
from . import library as lib, projects as proj

_running = Lock()


def _characters(text: str) -> list[str]:
    """Normalize case and width, and remove punctuation and whitespace for matching."""
    return [c for c in unicodedata.normalize("NFKC", text).casefold() if c.isalnum()]


def align_words(scenes: list, words: list[dict]) -> list[dict]:
    """Match scene sentences in source order using recognized words; omit times for weak matches."""
    heard, word_indices = [], []
    for index, word in enumerate(words):
        chars = _characters(word["text"])
        heard.extend(chars)
        word_indices.extend([index] * len(chars))
    script, ranges = [], []
    for scene in scenes:
        start = len(script)
        phrases = []
        for text in re.split(r"(?<=[。！？!?；;])|\n+", scene.narration):
            chars = _characters(text)
            if chars:
                phrases.append((text.strip(), len(script), len(script) + len(chars)))
                script.extend(chars)
        ranges.append((scene, start, len(script), phrases))
    matches = {}
    for block in SequenceMatcher(None, script, heard, autojunk=False).get_matching_blocks():
        # Isolated common characters are not reliable anchors for a longer script.
        if block.size >= 2 or len(script) == 1:
            matches.update((block.a + i, word_indices[block.b + i]) for i in range(block.size))

    def timing(start: int, end: int) -> dict:
        """Return source milliseconds and a review flag from the matched span and coverage."""
        indices = [matches[i] for i in range(start, end) if i in matches]
        coverage = len(indices) / max(1, end - start)
        matched = bool(indices) and coverage >= .55
        start_ms = words[indices[0]]["startMs"] if matched else None
        end_ms = words[indices[-1]]["endMs"] if matched else None
        status = "unmatched"
        if matched:
            span_count = len(_characters("".join(w["text"] for w in words[indices[0]:indices[-1]+1])))
            status = "matched" if coverage >= .85 and span_count <= (end-start)*1.4 and end_ms > start_ms else "review"
        return {"startMs":start_ms, "endMs":end_ms, "coverage":round(coverage, 2), "status":status}

    return [{"sceneId":scene.sceneId, **timing(start, end),
             "sentences":[{"text":text, **timing(a, b)} for text, a, b in phrases]}
            for scene, start, end, phrases in ranges]


def _transcribe(source: Path) -> list[dict]:
    """Load a cached local Whisper model and return audio-derived word estimates in milliseconds."""
    root = Path(__file__).resolve().parents[3]
    cached_runtime = root / ".tmp" / "asr-runtime"
    candidates = [
        Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe",
        Path.home() / "AppData/Local/Programs/Python/Python312/python.exe",
    ]
    override = os.environ.get("MOTION_STUDIO_ASR_PYTHON")
    runner = override or (next((str(p) for p in candidates if p.is_file()), sys.executable) if cached_runtime.is_dir() else sys.executable)
    env = {**os.environ, "HF_HUB_OFFLINE":"1"}
    completed = subprocess.run([runner, "-X", "utf8", str(root / "scripts/transcribe_narration.py"), str(source)],
                               env=env, capture_output=True, text=True, encoding="utf-8",
                               errors="replace", creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip().splitlines()[-1] if completed.stderr.strip() else "本地语音识别失败")
    return json.loads(completed.stdout)


def read_alignment(project_id: str) -> dict | None:
    """Read saved timestamps and flag them if the source storytelling revision has changed."""
    path = proj.project_dir(project_id) / "narration-alignment.json"
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    return {**data, "stale":data["storyboardRevision"] != proj.read_storyboard(project_id).projectRevision}


def align_project(project_id: str, asset_id: str, scope: str, revision: int) -> dict:
    """Transcribe a registered video, align current storyboard narration, and save a sidecar only."""
    if scope not in (project_id, "library"):
        raise ValueError("只能使用本项目或公共素材库的口播文件")
    storyboard = proj.read_storyboard(project_id)
    if storyboard.projectRevision != revision:
        raise PermissionError("分镜已更新，请刷新后再对齐")
    if not any(_characters(s.narration) for s in storyboard.scenes):
        raise ValueError("分镜中没有可对齐的口播稿")
    asset = next((a for a in lib.load_asset_registry(scope) if a.assetId == asset_id), None)
    if not asset or asset.mediaType not in ("video", "recording", "audio"):
        raise ValueError("请选择已登记的视频或音频")
    root = lib.projects_root().parent.resolve()
    allowed = (lib.assets_dir() if scope == "library" else proj.assets_dir_project(project_id)).resolve()
    source = (allowed / asset.localPath).resolve()
    if not source.is_relative_to(allowed) or not source.is_file():
        raise ValueError("口播素材文件不存在或不在指定素材库")
    if not _running.acquire(blocking=False):
        raise PermissionError("本地口播识别正在运行，请稍后重试")
    try:
        file = source.stat()
        source_key = [source.relative_to(root).as_posix(), file.st_size, file.st_mtime_ns]
        previous = read_alignment(project_id)
        words = previous["words"] if previous and previous.get("sourceKey") == source_key else _transcribe(source)
        if not words:
            raise ValueError("没有识别到可用于对齐的语音")
        if proj.read_storyboard(project_id).projectRevision != revision:
            raise PermissionError("识别期间分镜已更新，请刷新后重试")
        result = {"assetId":asset_id, "assetName":asset.name, "scope":scope, "sourceKey":source_key,
                  "storyboardRevision":revision, "updatedAt":now_iso(), "timeBasis":"source-audio-ms",
                  "words":words, "scenes":align_words(storyboard.scenes, words), "stale":False}
        atomic_write_json(proj.project_dir(project_id) / "narration-alignment.json", RootModel[dict](result))
        return result
    finally:
        _running.release()
