# Author: Codex | Created: 2026-11-24 20:27:24 +08:00 | Isolate the local Whisper native runtime from the workbench Python.
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys


def main(source: Path) -> None:
    """Write only recognized words and source timestamps to stdout; read local model weights."""
    runtime = Path(__file__).resolve().parents[1] / ".tmp/asr-runtime"
    if sys.version_info[:2] == (3, 12) and runtime.is_dir():
        sys.path.insert(0, str(runtime))
    cache = Path.home() / ".cache/huggingface/hub/models--Systran--faster-whisper-small"
    override = os.environ.get("MOTION_STUDIO_ASR_MODEL")
    ref = cache / "refs/main"
    model_path = Path(override) if override else cache / "snapshots" / (ref.read_text().strip() if ref.is_file() else "missing")
    if not (model_path / "model.bin").is_file():
        raise RuntimeError("未找到本地 Whisper 模型：请准备 faster-whisper-small 权重，或设置 MOTION_STUDIO_ASR_MODEL。")
    from faster_whisper import WhisperModel
    import numpy as np

    model = WhisperModel(str(model_path), device="cpu", compute_type="int8", cpu_threads=min(8, os.cpu_count() or 1), local_files_only=True)
    decoded = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(source), "-map", "0:a:0",
                              "-ac", "1", "-ar", "16000", "-f", "s16le", "pipe:1"],
                             capture_output=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if decoded.returncode or not decoded.stdout:
        raise RuntimeError("无法读取口播素材的音轨，请检查文件是否包含音频。")
    audio = np.frombuffer(decoded.stdout, dtype="<i2").astype(np.float32) / 32768
    segments, _ = model.transcribe(audio, language="zh", beam_size=5, word_timestamps=True,
                                   vad_filter=True, condition_on_previous_text=False)
    words = [{"text":word.word, "startMs":round(word.start*1000), "endMs":round(word.end*1000)}
             for segment in segments for word in segment.words or [] if word.start is not None and word.end is not None]
    print(json.dumps(words, ensure_ascii=False))


if __name__ == "__main__":
    os.environ["HF_HUB_OFFLINE"] = "1"
    main(Path(sys.argv[1]))
