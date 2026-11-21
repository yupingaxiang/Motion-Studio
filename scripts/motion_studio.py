# Author: Codex | Modified: 2026-11-21 23:55:00 +08:00 | Bind approved candidate props to rendering.
"""Motion Studio 本地 CLI。

Codex Desktop 通过本 Skill 调用此 CLI 完成本地数据操作、检索、验证与渲染调用。
此 CLI 不调用任何 AI 后端——视觉语义理解与候选选择由当前 Codex Agent 按 Skill 完成，
CLI 只负责查询库、写入结构化结果、触发渲染。

用法：
    python scripts/motion_studio.py init
    python scripts/motion_studio.py status --project demo-project
    python scripts/motion_studio.py validate --project demo-project
    python scripts/motion_studio.py search --query "关键词揭示" [--category TEXT] [--aspect 9:16]
    python scripts/motion_studio.py search-styles --query "极简科技"
    python scripts/motion_studio.py publish-recommendations --project demo-project --input <json>
    python scripts/motion_studio.py read-approvals --project demo-project
    python scripts/motion_studio.py render-template-previews
    python scripts/motion_studio.py render-scene-preview --project demo-project --scene <id>
    python scripts/motion_studio.py produce --project demo-project
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# 让脚本能在不安装为包的情况下导入 backend.app
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from backend.app.services import library as lib  # noqa: E402
from backend.app.services import projects as proj  # noqa: E402
from backend.app.models import (  # noqa: E402
    ApprovalStatus,
    Approvals,
    atomic_write_json,
    read_json_model,
    now_iso,
    Recommendations,
    SceneRecommendation,
    Storyboard,
    Scene,
)


# ---------------------------------------------------------------------------
# 工具
# ---------------------------------------------------------------------------


def _print_json(obj) -> None:
    print(json.dumps(obj, indent=2, ensure_ascii=False, default=str))


def _node_bin() -> str:
    """返回可用的 node 可执行文件路径。优先 DSH 捆绑，其次 PATH。"""
    dsh_node = Path(
        os.environ.get(
            "DSH_NODE",
            r"C:\Users\Administrator\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe",
        )
    )
    if dsh_node.exists():
        return str(dsh_node)
    return "node"


def _pnpm_bin() -> str:
    dsh_pnpm = Path(
        os.environ.get(
            "DSH_PNPM",
            r"C:\Users\Administrator\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\pnpm\bin\pnpm.mjs",
        )
    )
    if dsh_pnpm.exists():
        return str(dsh_pnpm)
    return "pnpm"


def _remotion_root() -> Path:
    return _ROOT / "remotion"


def _remotion_env() -> dict[str, str]:
    """返回带工作区内 TEMP 的环境变量，避免 Puppeteer 在系统 Temp 目录权限不足。

    Remotion render 通过 Puppeteer 启动 headless Chrome 渲染帧，
    Chrome 需要在临时目录创建 profile。某些受限环境下系统 Temp 不可写，
    因此把 TEMP/TMP 指向项目内 .tmp 目录。
    """
    env = os.environ.copy()
    tmp_dir = _ROOT / ".tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    pup_dir = tmp_dir / "puppeteer"
    pup_dir.mkdir(parents=True, exist_ok=True)
    env["TEMP"] = str(tmp_dir)
    env["TMP"] = str(tmp_dir)
    env["TMPDIR"] = str(tmp_dir)
    return env


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------


def cmd_init(args: argparse.Namespace) -> int:
    """初始化库 catalog、demo 项目、默认素材登记。"""
    print("[init] 扫描动效库与风格库，生成 catalog.json ...")
    p = lib.write_catalog()
    print(f"  catalog.json -> {p}")
    summary = lib.catalog_summary()
    print(f"  模板: {summary['totalTemplates']} 个 (approved {summary['approvedTemplates']})")
    print(f"  预览 MP4 存在: {summary['previewOk']}")
    if summary["previewMissing"]:
        print(f"  缺失预览: {summary['previewMissing']}")
    print(f"  风格: {summary['totalStyles']} 个")

    # 确保 demo 项目存在
    demo = proj.project_dir("demo-project")
    if not demo.exists():
        print("[init] 创建 demo-project 示例项目 ...")
        _init_demo_project()
    else:
        print(f"[init] demo-project 已存在: {demo}")

    # 确保目录
    for d in [lib.assets_dir(), proj.projects_root()]:
        d.mkdir(parents=True, exist_ok=True)

    print("[init] 完成。")
    return 0


def _init_demo_project() -> None:
    """创建 demo-project 的 storyboard（真实示例数据）。"""
    pd = proj.project_dir("demo-project")
    (pd / "assets").mkdir(parents=True, exist_ok=True)
    (pd / "previews").mkdir(parents=True, exist_ok=True)
    (pd / "output").mkdir(parents=True, exist_ok=True)

    script = (
        "大家好，今天介绍一个概念：复利。\n"
        "复利就是利滚利，收益会产生新的收益。\n"
        "举个例子，每天进步百分之一，一年后会变成原来的三十七倍。\n"
        "左侧是单利，右侧是复利，对比非常明显。\n"
        "关键在于坚持，时间会放大每一次小小的进步。\n"
        "这就是复利的力量。"
    )
    scenes = [
        Scene(
            sceneId="S01",
            narration="大家好，今天介绍一个概念：复利。",
            startMs=0,
            endMs=3000,
            visualIntent="开场标题：关键词「复利」揭示，极简科技风格",
            styleId="minimal-tech",
        ),
        Scene(
            sceneId="S02",
            narration="复利就是利滚利，收益会产生新的收益。",
            startMs=3000,
            endMs=7500,
            visualIntent="流程节点展开：本金→收益→新本金→新收益 的循环",
            styleId="minimal-tech",
        ),
        Scene(
            sceneId="S03",
            narration="举个例子，每天进步百分之一，一年后会变成原来的三十七倍。",
            startMs=7500,
            endMs=13500,
            visualIntent="数字与趋势变化：1.01 的 365 次方增长曲线与最终数字 37.78",
            styleId="blueprint",
        ),
        Scene(
            sceneId="S04",
            narration="左侧是单利，右侧是复利，对比非常明显。",
            startMs=13500,
            endMs=18000,
            visualIntent="左右概念对比：单利线性增长 vs 复利指数增长",
            styleId="blueprint",
        ),
        Scene(
            sceneId="S05",
            narration="关键在于坚持，时间会放大每一次小小的进步。",
            startMs=18000,
            endMs=22500,
            visualIntent="数据强调：时间轴上小步累积被放大的视觉",
            styleId="minimal-tech",
        ),
        Scene(
            sceneId="S06",
            narration="这就是复利的力量。",
            startMs=22500,
            endMs=26000,
            visualIntent="章节过渡到结尾卡片：复利的力量",
            styleId="minimal-tech",
        ),
    ]
    sb = Storyboard(
        projectId="demo-project",
        projectRevision=1,
        script=script,
        scenes=scenes,
        updatedAt=now_iso(),
    )
    proj.write_storyboard(sb)


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------


def cmd_status(args: argparse.Namespace) -> int:
    if args.project:
        if not proj.project_exists(args.project):
            print(f"项目不存在: {args.project}")
            return 1
        s = proj.project_status(args.project)
        _print_json(s)
    else:
        # 全局状态
        cat = lib.catalog_summary()
        projects = proj.list_projects()
        _print_json(
            {
                "library": cat,
                "projects": projects,
            }
        )
    return 0


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------


def cmd_validate(args: argparse.Namespace) -> int:
    if not proj.project_exists(args.project):
        print(f"项目不存在: {args.project}")
        return 1
    res = proj.validate_project(args.project)
    _print_json(res)
    return 0 if res["valid"] else 1


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------


def cmd_search(args: argparse.Namespace) -> int:
    results = lib.search_templates(
        args.query or "",
        category=args.category,
        aspect_ratio=args.aspect,
        tags=args.tags.split(",") if args.tags else None,
        require_assets=args.assets.split(",") if args.assets else None,
        limit=args.limit,
    )
    out = []
    for meta, score in results:
        preview = lib.template_preview_abs(meta.templateId)
        out.append(
            {
                "templateId": meta.templateId,
                "name": meta.name,
                "version": meta.version,
                "category": meta.category,
                "score": round(score, 3),
                "previewMp4": str(preview) if preview else None,
                "previewExists": bool(preview),
                "sourceAvailable": meta.sourceAvailable,
                "sourceName": meta.sourceName,
                "sourceUrl": meta.sourceUrl,
                "originalId": meta.originalId,
                "adaptation": meta.adaptation,
                "useCases": meta.useCases,
                "notUseCases": meta.notUseCases,
                "durationFrames": meta.durationFrames,
                "requiredAssets": meta.requiredAssets,
                "params": [p.model_dump() for p in meta.params],
            }
        )
    _print_json({"query": args.query, "count": len(out), "results": out})
    return 0


def cmd_search_styles(args: argparse.Namespace) -> int:
    results = lib.search_styles(args.query or "", limit=args.limit)
    out = []
    for s, score in results:
        out.append(
            {
                "styleId": s.styleId,
                "name": s.name,
                "description": s.description,
                "score": round(score, 3),
                "colors": [c.model_dump() for c in s.colors],
                "recommendedScenes": s.recommendedScenes,
                "forbiddenScenes": s.forbiddenScenes,
            }
        )
    _print_json({"query": args.query, "count": len(out), "results": out})
    return 0


# ---------------------------------------------------------------------------
# publish-recommendations
# ---------------------------------------------------------------------------


def cmd_publish_recommendations(args: argparse.Namespace) -> int:
    """Codex 按 Skill 完成视觉理解与候选选择后，调用此命令将结果写入 recommendations.json。

    --input 指向一个 JSON 文件，结构与 Recommendations 一致（projectId/scenes/candidates）。
    此命令执行冲突校验：已 APPROVED 且未要求重选的分镜拒绝覆盖。
    """
    if not proj.project_exists(args.project):
        print(f"项目不存在: {args.project}")
        return 1
    inp = Path(args.input)
    if not inp.exists():
        print(f"输入文件不存在: {inp}")
        return 1
    with inp.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    # 强制 projectId 一致
    raw["projectId"] = args.project
    # 校验候选 previewPath 真实存在
    pd = proj.project_dir(args.project)
    for sr in raw.get("scenes", []):
        for c in sr.get("candidates", []):
            pp = c.get("previewPath", "")
            p = Path(pp) if Path(pp).is_absolute() else _ROOT / pp
            if not p.exists():
                print(f"[错误] 候选 {c.get('templateId')} 的 previewPath 不存在: {p}")
                print("       所有候选必须指向真实存在的本地 MP4。")
                return 1
    recs = Recommendations.model_validate(raw)
    # 自动递增 revision
    try:
        old = proj.read_recommendations(args.project)
        recs.recommendationRevision = old.recommendationRevision + 1
    except FileNotFoundError:
        recs.recommendationRevision = 1
    try:
        sb = proj.read_storyboard(args.project)
        recs.basedOnStoryboardRevision = sb.projectRevision
    except FileNotFoundError:
        pass
    recs.updatedAt = now_iso()
    try:
        p = proj.write_recommendations(recs)
    except PermissionError as e:
        print(f"[拒绝] {e}")
        return 2
    print(f"[publish-recommendations] 已写入 recommendations rev {recs.recommendationRevision} -> {p}")
    # 输出每个分镜的候选摘要
    for sr in recs.scenes:
        print(
            f"  分镜 {sr.sceneId}: {len(sr.candidates)} 个候选 "
            f"{[c.templateId for c in sr.candidates]}"
        )
    return 0


# ---------------------------------------------------------------------------
# read-approvals
# ---------------------------------------------------------------------------


def cmd_read_approvals(args: argparse.Namespace) -> int:
    if not proj.project_exists(args.project):
        print(f"项目不存在: {args.project}")
        return 1
    app = proj.read_approvals_safe(args.project)
    _print_json(app.model_dump())
    return 0


# ---------------------------------------------------------------------------
# render-template-previews
# ---------------------------------------------------------------------------


def cmd_render_template_previews(args: argparse.Namespace) -> int:
    """批量渲染所有模板的 preview.mp4 与 poster.jpg。

    使用 Remotion CLI 渲染每个模板的 demo composition。
    需要先在 remotion/ 目录 pnpm install。
    """
    rr = _remotion_root()
    if not (rr / "package.json").exists():
        print(f"[错误] remotion 项目不存在: {rr}")
        return 1
    templates = lib.load_all_templates(include_deprecated=True)
    if args.only:
        templates = [t for t in templates if t.templateId == args.only]
    if not templates:
        print("没有模板可渲染。")
        return 1
    node = _node_bin()
    pnpm = _pnpm_bin()
    # 确保 node_modules
    if not (rr / "node_modules").exists():
        print("[render] 安装 remotion 依赖 ...")
        r = subprocess.run([node, pnpm, "install", "--no-frozen-lockfile"], cwd=str(rr))
        if r.returncode != 0:
            print("[错误] pnpm install 失败")
            return r.returncode
    ok, fail = 0, 0
    for meta in templates:
        td = lib.motions_dir() / meta.templateId
        td.mkdir(parents=True, exist_ok=True)
        mp4 = td / "preview.mp4"
        poster = td / "poster.jpg"
        if mp4.exists() and not args.force:
            print(f"  [{meta.templateId}] 已存在 preview.mp4，跳过（--force 可重渲染）")
            ok += 1
            continue
        print(f"  [{meta.templateId}] 渲染 {meta.compositionId} ...")
        cmd = [
            node,
            os.path.join("node_modules", "@remotion", "cli", "remotion-cli.js"),
            "render",
            meta.compositionId,
            str(mp4),
            "--codec=h264",
            "--concurrency=2",
        ]
        r = subprocess.run(cmd, cwd=str(rr), capture_output=True, text=True, encoding="utf-8", errors="replace", env=_remotion_env())
        if r.returncode != 0:
            print(f"    [失败] {meta.templateId}")
            print(r.stderr[-800:])
            fail += 1
            continue
        # 生成 poster：取第 1 秒帧
        poster_cmd = [
            node,
            os.path.join("node_modules", "@remotion", "cli", "remotion-cli.js"),
            "still",
            meta.compositionId,
            str(poster),
            "--frame=15",
        ]
        subprocess.run(poster_cmd, cwd=str(rr), capture_output=True, text=True, encoding="utf-8", errors="replace", env=_remotion_env())
        ok += 1
        print(f"    [完成] {mp4.name} + {poster.name}")
    print(f"[render-template-previews] 完成: {ok} 成功, {fail} 失败")
    # 重新生成 catalog
    lib.write_catalog()
    return 0 if fail == 0 else 1


# ---------------------------------------------------------------------------
# render-scene-preview
# ---------------------------------------------------------------------------


def cmd_render_scene_preview(args: argparse.Namespace) -> int:
    """渲染单个分镜的适配预览（Scene Preview）。

    读取该分镜已选中的模板与 storyboard 内容，生成 props，渲染到 projects/<p>/previews/。
    缓存键 = sceneId + templateVersion + propsHash + assetHash。
    """
    if not proj.project_exists(args.project):
        print(f"项目不存在: {args.project}")
        return 1
    sb = proj.read_storyboard(args.project)
    scene = next((s for s in sb.scenes if s.sceneId == args.scene), None)
    if scene is None:
        print(f"分镜不存在: {args.scene}")
        return 1
    app = proj.read_approvals_safe(args.project)
    ap = next((a for a in app.approvals if a.sceneId == args.scene), None)
    if ap is None or not ap.selectedTemplateId:
        print(f"分镜 {args.scene} 尚未选中模板，无法渲染场景预览。")
        print("提示：用户需先在 Web 工作台 SELECTED 一个候选。")
        return 1
    meta = lib.get_template(ap.selectedTemplateId)
    if meta is None:
        print(f"模板 {ap.selectedTemplateId} 不存在")
        return 1
    # 构建 props（基于分镜内容）
    props = _build_scene_props(scene, meta, _selected_candidate_props(args.project, scene.sceneId, ap))
    import hashlib

    props_hash = hashlib.sha256(
        json.dumps({"scene": scene.model_dump(), "props": props}, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()[:12]
    cache_key = f"{args.scene}_{meta.templateId}_v{meta.version.replace('.', '-')}_{props_hash}"
    out_mp4 = proj.previews_dir(args.project) / f"{cache_key}.mp4"
    poster = proj.previews_dir(args.project) / f"{cache_key}.jpg"

    if out_mp4.exists() and not args.force:
        print(f"[scene-preview] 缓存命中: {out_mp4}")
        return 0

    node = _node_bin()
    rr = _remotion_root()
    # 把 props 写到临时 input props 文件
    props_file = proj.previews_dir(args.project) / f"{cache_key}.props.json"
    props_data = {
        "sceneId": scene.sceneId,
        "narration": scene.narration,
        "templateId": meta.templateId,
        "styleId": scene.styleId,
        "durationFrames": meta.durationFrames,
        **props,
    }
    composition_id = meta.compositionId
    if props.get("_editor"):
        editor = props["_editor"]
        props_data = {"templateId":meta.templateId,"content":{k:v for k,v in props.items() if k!="_editor"},"sceneDurationMs":scene.endMs-scene.startMs,**editor}
        composition_id = "SCENE-EDIT"
    props_file.parent.mkdir(parents=True, exist_ok=True)
    props_file.write_text(json.dumps(props_data, ensure_ascii=False, indent=2), encoding="utf-8")

    cmd = [
        node,
        os.path.join("node_modules", "@remotion", "cli", "remotion-cli.js"),
        "render",
        composition_id,
        str(out_mp4),
        "--codec=h264",
        "--props",
        str(props_file),
        "--concurrency=2",
    ]
    print(f"[scene-preview] 渲染 {meta.compositionId} props={props_file.name}")
    r = subprocess.run(cmd, cwd=str(rr), capture_output=True, text=True, encoding="utf-8", errors="replace", env=_remotion_env())
    if r.returncode != 0:
        print(f"[失败] {(r.stderr or '')[-1000:]}")
        return r.returncode
    # poster
    poster_cmd = [
        node,
        os.path.join("node_modules", "@remotion", "cli", "remotion-cli.js"),
        "still",
        composition_id,
        str(poster),
        "--frame=15",
        "--props",
        str(props_file),
    ]
    subprocess.run(poster_cmd, cwd=str(rr), capture_output=True, text=True, encoding="utf-8", errors="replace", env=_remotion_env())
    # 更新 approvals 的 preview 记录（可选元数据）
    print(f"[scene-preview] 完成: {out_mp4}")
    # 写一条 preview manifest
    manifest = proj.previews_dir(args.project) / "manifest.json"
    entries = []
    if manifest.exists():
        entries = json.loads(manifest.read_text(encoding="utf-8"))
    entries = [e for e in entries if e.get("cacheKey") != cache_key]
    entries.append(
        {
            "cacheKey": cache_key,
            "storyboardRevision": sb.projectRevision,
            "sceneId": args.scene,
            "templateId": meta.templateId,
            "templateVersion": meta.version,
            "propsHash": props_hash,
            "mp4": out_mp4.name,
            "poster": poster.name if poster.exists() else "",
            "createdAt": now_iso(),
        }
    )
    manifest.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


def _scene_media_props(scene) -> dict:
    """Stage a bound background image with a content-addressed identity for deterministic renders.

    Reject missing or out-of-workspace media. Copies are cached under Remotion public.
    """
    import hashlib
    import shutil
    from pathlib import Path
    root = lib.library_root().parent.resolve()
    for ref in getattr(scene, "assets", []):
        if ref.role != "background" or not ref.localPath:
            continue
        source = (root / ref.localPath).resolve()
        if not source.is_relative_to(root) or source.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"):
            raise ValueError("Background image must be a local workspace image")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        name = digest + source.suffix.lower()
        target = _remotion_root() / "public" / "scene-assets" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copyfile(source, target)
        return {"backgroundImage": "scene-assets/" + name, "assetIdentity": digest}
    return {}


def _stage_presenter_source(scene, props: dict) -> str:
    """Stage a local presenter video and reject missing footage, unsafe paths or insufficient duration."""
    import hashlib,shutil
    raw=props.get("presenterSrc","")
    if not raw:raise ValueError("真人转场正式渲染需要选择真实口播视频，演示人物仅用于模板预览")
    if not isinstance(raw,str) or raw.startswith(("/","\\","http:","https:")) or ".." in raw.replace("\\","/").split("/"):
        raise ValueError("口播视频必须使用本地项目素材或 Remotion public 相对路径")
    root=lib.library_root().parent.resolve() if raw.startswith(("projects/","library/")) else (_remotion_root()/"public").resolve()
    source=(root/raw).resolve()
    if not source.is_relative_to(root) or not source.is_file() or source.suffix.lower() not in (".mp4",".mov",".webm",".mkv"):
        raise ValueError("口播视频文件不存在或类型无效")
    probe=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","json",str(source)],capture_output=True,text=True,encoding="utf-8")
    if probe.returncode:raise ValueError("无法读取口播视频时长")
    start=props.get("sourceStartFrame",0)
    import math
    if isinstance(start,bool) or not isinstance(start,(int,float)) or not math.isfinite(start) or start<0 or int(start)!=start:raise ValueError("源视频起始帧必须是非负整数")
    required=start/30+math.ceil((scene.endMs-scene.startMs)*.03)/30
    if float(json.loads(probe.stdout)["format"]["duration"])+.001<required:raise ValueError("口播视频剩余时长不足，不能冻结尾帧代替真实口播")
    name=hashlib.sha256(source.read_bytes()).hexdigest()+source.suffix.lower()
    target=_remotion_root()/"public"/"scene-assets"/name
    target.parent.mkdir(parents=True,exist_ok=True)
    if not target.exists():shutil.copyfile(source,target)
    return "scene-assets/"+name


def _selected_candidate_props(project_id, scene_id, approval) -> dict:
    """Resolve the selected candidate by ID and version; missing recommendations yield defaults."""
    try:
        recs = proj.read_recommendations(project_id)
    except FileNotFoundError:
        return {}
    for scene_rec in recs.scenes:
        if scene_rec.sceneId == scene_id:
            for candidate in scene_rec.candidates:
                if (candidate.templateId == approval.selectedTemplateId
                        and candidate.templateVersion == approval.selectedTemplateVersion):
                    result = dict(candidate.proposedProps)
                    saved = proj.read_scene_edits(project_id)["scenes"].get(scene_id)
                    if saved:
                        if saved["templateId"] != approval.selectedTemplateId or saved["templateVersion"] != approval.selectedTemplateVersion:
                            raise ValueError("Manual edit template/version differs from selected candidate; update recommendations and review explicitly")
                        result.update(saved["props"])
                        result["_editor"] = {k:saved[k] for k in ("startMs","endMs","layout","elements") if k in saved}
                    return result
    return {}


def _build_scene_props(scene, meta, proposed_props: dict | None = None) -> dict:
    """Build candidate props and route bound backgrounds through the shared full-scene renderer."""
    props: dict = {}
    # 通用：narration 作为文本来源
    if meta.templateId.startswith("TEXT"):
        # 提取关键词：取 narration 中第一个引号或冒号后的词，或最长词
        text = scene.narration
        # 简单：用 narration 的核心词
        keyword = scene.visualIntent.split("：")[-1].split(":")[-1].strip() or scene.narration[:6]
        props["keyword"] = keyword
        props["subtitle"] = scene.narration
    elif meta.templateId.startswith("FLOW"):
        props["nodes"] = ["本金", "收益", "新本金", "新收益"]
        props["title"] = scene.narration[:20]
    elif meta.templateId.startswith("COMP"):
        props["leftLabel"] = "单利"
        props["rightLabel"] = "复利"
        props["leftValue"] = "线性"
        props["rightValue"] = "指数"
    elif meta.templateId.startswith("DATA"):
        props["startValue"] = "1.00"
        props["endValue"] = "37.78"
        props["caption"] = scene.narration[:30]
    elif meta.templateId.startswith("TRANS"):
        props["title"] = scene.narration[:12]
    elif meta.templateId.startswith("DEMO"):
        props["caption"] = scene.narration[:20]
        props["steps"] = ["步骤一", "步骤二", "步骤三"]
    # 应用模板默认参数（补全未显式设置的）
    for param in meta.params:
        if param.name not in props:
            val = param.default
            # steps/nodes 等数组型参数，若 default 是逗号字符串则转数组
            if param.name in ("steps", "nodes") and isinstance(val, str):
                val = [s.strip() for s in val.split(",") if s.strip()]
            props[param.name] = val
    if proposed_props:
        props.update(proposed_props)
    props["styleId"] = scene.styleId
    props.update(_scene_media_props(scene))
    if meta.templateId.startswith("PRESENTER-"):
        props["presenterSrc"]=_stage_presenter_source(scene,props)
        props.setdefault("_editor",{"startMs":0,"endMs":scene.endMs-scene.startMs,"layout":{"x":0,"y":0,"scale":1,"transparent":False}})
        editor=props["_editor"]
        if editor["startMs"]!=0 or editor["endMs"]!=scene.endMs-scene.startMs or any(editor["layout"].get(k,default)!=default for k,default in (("x",0),("y",0),("scale",1))):
            raise ValueError("真人转场必须覆盖整段且保持全屏终点；请调整人物小窗参数")
        if meta.templateId=="PRESENTER-OUT" and props.get("transitionAt",60)<24:raise ValueError("需预留24帧收起知识卡片")
        available=(props["_editor"]["endMs"]-props["_editor"]["startMs"])*.03
        if props.get("transitionAt",30 if meta.templateId=="PRESENTER-IN" else 60)+props.get("transitionFrames",26)>available-1:
            raise ValueError("真人转场时间超出动效出现区间，请调整开始帧或延长区间")
    if props.get("backgroundImage") and not props.get("_editor"):
        props["_editor"]={"startMs":0,"endMs":scene.endMs-scene.startMs,"layout":{"x":0,"y":0,"scale":1,"transparent":False}}
    return props


# ---------------------------------------------------------------------------
# produce
# ---------------------------------------------------------------------------


def cmd_produce(args: argparse.Namespace) -> int:
    """合成最终视频。要求所有分镜已确认（APPROVED 或 NO_MOTION）。"""
    if not proj.project_exists(args.project):
        print(f"项目不存在: {args.project}")
        return 1
    status = proj.project_status(args.project)
    if not status["allConfirmed"]:
        print("[拒绝] 未获用户确认，不得正式渲染完整成片。")
        print(f"  分镜总数: {status['sceneCount']}")
        print(f"  已确认: {status['approvedCount']} + 无需动效 {status['noMotionCount']}")
        print(f"  待确认/选中/重选: {status['pendingCount']}/{status['selectedCount']}/{status['reselectCount']}")
        print("  请在 Web 工作台完成所有分镜的确认。")
        return 2
    print("[produce] 所有分镜已确认，开始合成 ...")
    sb = proj.read_storyboard(args.project)
    app = proj.read_approvals_safe(args.project)
    node = _node_bin()
    rr = _remotion_root()
    # 为每个 APPROVED 分镜渲染场景预览
    timeline_inputs: list[dict] = []
    for scene in sb.scenes:
        ap = next((a for a in app.approvals if a.sceneId == scene.sceneId), None)
        if ap is None or ap.approvalStatus == ApprovalStatus.NO_MOTION.value:
            continue
        if ap.approvalStatus != ApprovalStatus.APPROVED.value:
            continue
        meta = lib.get_template(ap.selectedTemplateId)
        if meta is None:
            print(f"[警告] 分镜 {scene.sceneId} 模板 {ap.selectedTemplateId} 缺失，跳过")
            continue
        props = _build_scene_props(scene, meta, _selected_candidate_props(args.project, scene.sceneId, ap))
        props_data = {
            "sceneId": scene.sceneId,
            "narration": scene.narration,
            "templateId": meta.templateId,
            "styleId": scene.styleId,
            "durationFrames": meta.durationFrames,
            **props,
        }
        clip_mp4 = proj.previews_dir(args.project) / f"{scene.sceneId}_final.mp4"
        props_file = proj.previews_dir(args.project) / f"{scene.sceneId}_final.props.json"
        composition_id = meta.compositionId
        if props.get("_editor"):
            props_data = {"templateId":meta.templateId,"content":{k:v for k,v in props.items() if k!="_editor"},"sceneDurationMs":scene.endMs-scene.startMs,**props["_editor"]}
            composition_id = "SCENE-EDIT"
        props_file.write_text(json.dumps(props_data, ensure_ascii=False, indent=2), encoding="utf-8")
        cmd = [
            node,
            os.path.join("node_modules", "@remotion", "cli", "remotion-cli.js"),
            "render",
            composition_id,
            str(clip_mp4),
            "--codec=h264",
            "--props",
            str(props_file),
            "--concurrency=2",
        ]
        print(f"  [clip] {scene.sceneId} -> {meta.templateId}")
        r = subprocess.run(cmd, cwd=str(rr), capture_output=True, text=True, encoding="utf-8", errors="replace", env=_remotion_env())
        if r.returncode != 0:
            print(f"    [失败] {r.stderr[-800:]}")
            return r.returncode
        timeline_inputs.append({"sceneId": scene.sceneId, "mp4": str(clip_mp4), "durationMs": scene.endMs - scene.startMs})

    # 用 ffmpeg 拼接
    out_mp4 = proj.output_dir(args.project) / f"{args.project}_final.mp4"
    proj.output_dir(args.project).mkdir(parents=True, exist_ok=True)
    if not timeline_inputs:
        print("[produce] 无可合成片段（全部 NO_MOTION）。生成空白占位。")
        # 生成 1 秒黑场
        subprocess.run(
            [
                "ffmpeg", "-y", "-f", "lavfi", "-i",
                "color=c=black:s=1080x1920:d=1", "-r", "30",
                str(out_mp4),
            ],
            capture_output=True,
        )
    else:
        # concat demuxer
        concat_list = proj.output_dir(args.project) / "concat.txt"
        lines = [f"file '{ti['mp4']}'" for ti in timeline_inputs]
        concat_list.write_text("\n".join(lines), encoding="utf-8")
        ff = subprocess.run(
            [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", str(concat_list), "-c", "copy", str(out_mp4),
            ],
            capture_output=True,
            text=True,
        )
        if ff.returncode != 0:
            # copy 失败则重编码
            print("  [concat] copy 失败，重编码 ...")
            ff2 = subprocess.run(
                [
                    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", str(concat_list), "-c:v", "libx264",
                    "-preset", "fast", "-r", "30",
                    "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,"
                    "pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
                    str(out_mp4),
                ],
                capture_output=True,
                text=True,
            )
            if ff2.returncode != 0:
                print(f"  [失败] ffmpeg: {ff2.stderr[-800:]}")
                return ff2.returncode
    print(f"[produce] 最终视频: {out_mp4}")
    # 验证产物
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration,size:stream=width,height,codec_name,r_frame_rate",
         "-of", "json", str(out_mp4)],
        capture_output=True,
        text=True,
    )
    if probe.returncode == 0:
        info = json.loads(probe.stdout)
        print(f"[produce] 音视频校验: {json.dumps(info, ensure_ascii=False)}")
    return 0


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def cmd_review_brief(args: argparse.Namespace) -> int:
    """Print the project handoff packet for the current AI conversation without mutating files."""
    _print_json(proj.review_brief(args.project))
    return 0


def cmd_publish_storyboard(args: argparse.Namespace) -> int:
    """Publish AI-parsed storyboard JSON with revision and locked-scene protection."""
    incoming = read_json_model(Path(args.input), Storyboard)
    if incoming.projectId != args.project:
        print("Project ID mismatch")
        return 2
    try:
        previous = proj.read_storyboard(args.project)
    except FileNotFoundError:
        previous = None
    current_revision = previous.projectRevision if previous else 0
    if current_revision != args.expected_revision:
        print("Storyboard revision conflict; read review-brief before retrying")
        return 2
    if previous:
        approvals = proj.read_approvals_safe(args.project)
        locked = {a.sceneId for a in approvals.approvals if a.locked}
        for old in previous.scenes:
            new = next((n for n in incoming.scenes if n.sceneId == old.sceneId), None)
            if old.sceneId in locked and (new is None or new.model_dump() != old.model_dump()):
                print(f"Locked scene cannot be changed: {old.sceneId}")
                return 2
    ids = [scene.sceneId for scene in incoming.scenes]
    if len(ids) != len(set(ids)) or any(scene.endMs <= scene.startMs or scene.startMs < 0 for scene in incoming.scenes):
        print("Invalid duplicate scene IDs or timing")
        return 2
    incoming.projectRevision = current_revision + 1
    proj.write_storyboard(incoming)
    _print_json({"projectId":args.project,"projectRevision":incoming.projectRevision,"sceneCount":len(ids)})
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="motion_studio",
        description="Motion Studio 本地 CLI（Codex Skill 调用）",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="初始化库 catalog 与 demo 项目").set_defaults(func=cmd_init)

    sp = sub.add_parser("status", help="查看库或项目状态")
    sp.add_argument("--project", default=None)
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("validate", help="校验项目数据一致性")
    sp.add_argument("--project", required=True)
    sp.set_defaults(func=cmd_validate)

    sp = sub.add_parser("search", help="检索动效模板（语义匹配）")
    sp.add_argument("--query", default="")
    sp.add_argument("--category", default=None)
    sp.add_argument("--aspect", default=None)
    sp.add_argument("--tags", default=None, help="逗号分隔")
    sp.add_argument("--assets", default=None, help="所需素材类型，逗号分隔")
    sp.add_argument("--limit", type=int, default=10)
    sp.set_defaults(func=cmd_search)

    sp = sub.add_parser("search-styles", help="检索视觉风格")
    sp.add_argument("--query", default="")
    sp.add_argument("--limit", type=int, default=5)
    sp.set_defaults(func=cmd_search_styles)

    sp = sub.add_parser("publish-recommendations", help="Codex 写入候选推荐（含冲突校验）")
    sp.add_argument("--project", required=True)
    sp.add_argument("--input", required=True, help="推荐 JSON 文件路径")
    sp.set_defaults(func=cmd_publish_recommendations)

    sp = sub.add_parser("publish-storyboard", help="Publish storyboard JSON parsed by the current AI")
    sp.add_argument("--project", required=True)
    sp.add_argument("--input", required=True)
    sp.add_argument("--expected-revision", type=int, required=True)
    sp.set_defaults(func=cmd_publish_storyboard)

    sp = sub.add_parser("review-brief", help="Read scenes, selections, feedback and next action for AI")
    sp.add_argument("--project", required=True)
    sp.set_defaults(func=cmd_review_brief)

    sp = sub.add_parser("read-approvals", help="读取用户审核结果")
    sp.add_argument("--project", required=True)
    sp.set_defaults(func=cmd_read_approvals)

    sp = sub.add_parser("render-template-previews", help="批量渲染所有模板 preview.mp4")
    sp.add_argument("--only", default=None, help="仅渲染指定 templateId")
    sp.add_argument("--force", action="store_true")
    sp.set_defaults(func=cmd_render_template_previews)

    sp = sub.add_parser("render-scene-preview", help="渲染单分镜适配预览")
    sp.add_argument("--project", required=True)
    sp.add_argument("--scene", required=True)
    sp.add_argument("--force", action="store_true")
    sp.set_defaults(func=cmd_render_scene_preview)

    sp = sub.add_parser("produce", help="合成最终视频（要求全部确认）")
    sp.add_argument("--project", required=True)
    sp.set_defaults(func=cmd_produce)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
