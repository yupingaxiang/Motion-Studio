# Author: Codex | Modified: 2026-11-21 23:55:00 +08:00 | Project media binding.
"""项目管理服务：storyboard / recommendations / approvals 的读写，
含版本号、原子写入与冲突校验，防止 Codex 与 Web 同时写损坏数据。

关键规则：
- approvals.json 由 Web 写入。APPROVED 后该分镜 locked=True，
  Codex 重新推荐时不可静默覆盖已确认选择。
- recommendations.json 由 Codex 写入。每次写入 recommendationRevision +1。
- 当用户要求 RECOMMEND_AGAIN 时，Codex 才生成新 revision 的候选；
  此时若该分镜已 APPROVED 且用户未明确要求重选，Codex 必须拒绝覆盖。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..models import (
    ApprovalStatus,
    Approvals,
    atomic_write_json,
    now_iso,
    read_json_model,
    Recommendations,
    SceneApproval,
    SceneRecommendation,
    Storyboard,
)
from .library import projects_root


# ---------------------------------------------------------------------------
# 路径
# ---------------------------------------------------------------------------


def project_dir(project_id: str) -> Path:
    return projects_root() / project_id


def storyboard_path(project_id: str) -> Path:
    return project_dir(project_id) / "storyboard.json"


def recommendations_path(project_id: str) -> Path:
    return project_dir(project_id) / "recommendations.json"


def approvals_path(project_id: str) -> Path:
    return project_dir(project_id) / "approvals.json"


def previews_dir(project_id: str) -> Path:
    return project_dir(project_id) / "previews"


def output_dir(project_id: str) -> Path:
    return project_dir(project_id) / "output"


def assets_dir_project(project_id: str) -> Path:
    return project_dir(project_id) / "assets"


def list_projects() -> list[str]:
    root = projects_root()
    if not root.exists():
        return []
    out = []
    for d in sorted(root.iterdir()):
        if d.is_dir() and (d / "storyboard.json").exists():
            out.append(d.name)
    return out


def project_exists(project_id: str) -> bool:
    return project_dir(project_id).exists()


# ---------------------------------------------------------------------------
# Storyboard
# ---------------------------------------------------------------------------


def read_storyboard(project_id: str) -> Storyboard:
    return read_json_model(storyboard_path(project_id), Storyboard)  # type: ignore[return-value]


def write_storyboard(sb: Storyboard) -> Path:
    sb.updatedAt = now_iso()
    p = storyboard_path(sb.projectId)
    p.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(p, sb)
    return p


def bump_storyboard_revision(project_id: str) -> int:
    sb = read_storyboard(project_id)
    sb.projectRevision += 1
    write_storyboard(sb)
    return sb.projectRevision


# ---------------------------------------------------------------------------
# Recommendations
# ---------------------------------------------------------------------------


def read_recommendations(project_id: str) -> Recommendations:
    return read_json_model(recommendations_path(project_id), Recommendations)  # type: ignore[return-value]


def recommendations_revision(project_id: str) -> int:
    try:
        return read_recommendations(project_id).recommendationRevision
    except FileNotFoundError:
        return 0


def write_recommendations(recs: Recommendations) -> Path:
    """Codex 写入推荐。若某分镜已 APPROVED 且非用户要求重选，拒绝覆盖。"""
    # 冲突校验：读取现有 approvals
    approvals = read_approvals_safe(recs.projectId)
    locked_scenes = {
        a.sceneId for a in approvals.approvals if a.locked and a.approvalStatus == ApprovalStatus.APPROVED.value
    }
    for scene_rec in recs.scenes:
        if scene_rec.sceneId in locked_scenes:
            # 检查该分镜是否处于 RECOMMEND_AGAIN（用户明确要求重选）
            ap = next((a for a in approvals.approvals if a.sceneId == scene_rec.sceneId), None)
            if ap and ap.approvalStatus == ApprovalStatus.RECOMMEND_AGAIN.value:
                # 用户要求重选，允许覆盖，但记录原选择以便回滚
                continue
            raise PermissionError(
                f"分镜 {scene_rec.sceneId} 已确认（APPROVED），"
                f"用户未要求重新选择，Codex 不可静默覆盖其候选。"
            )
    recs.updatedAt = now_iso()
    p = recommendations_path(recs.projectId)
    p.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(p, recs)
    return p


def next_recommendation_revision(project_id: str) -> int:
    return recommendations_revision(project_id) + 1


# ---------------------------------------------------------------------------
# Approvals —— Web 写入
# ---------------------------------------------------------------------------


def read_approvals(project_id: str) -> Approvals:
    return read_json_model(approvals_path(project_id), Approvals)  # type: ignore[return-value]


def read_approvals_safe(project_id: str) -> Approvals:
    """文件不存在时返回空 Approvals。"""
    try:
        return read_approvals(project_id)
    except FileNotFoundError:
        return Approvals(projectId=project_id, approvals=[], updatedAt=now_iso())


def _save_approvals(app: Approvals) -> Approvals:
    app.updatedAt = now_iso()
    p = approvals_path(app.projectId)
    p.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(p, app)
    return app


def select_candidate(
    project_id: str,
    scene_id: str,
    template_id: str,
    template_version: str,
    based_on_rev: int,
) -> Approvals:
    """用户选中某候选（SELECTED，尚未确认）。这是独立于确认的操作。"""
    app = read_approvals_safe(project_id)
    existing = next((a for a in app.approvals if a.sceneId == scene_id), None)
    if existing and existing.locked:
        raise PermissionError(
            f"分镜 {scene_id} 已确认锁定，无法更改选择。需用户明确要求重新选择。"
        )
    ap = existing or SceneApproval(sceneId=scene_id, basedOnRecommendationRevision=based_on_rev)
    ap.selectedTemplateId = template_id
    ap.selectedTemplateVersion = template_version
    ap.approvalStatus = ApprovalStatus.SELECTED.value
    ap.basedOnRecommendationRevision = based_on_rev
    ap.approvedAt = ""
    ap.locked = False
    if existing is None:
        app.approvals.append(ap)
    return _save_approvals(app)


def approve_scene(project_id: str, scene_id: str) -> Approvals:
    """确认分镜：将 SELECTED 提升为 APPROVED 并锁定。要求已选中。"""
    app = read_approvals_safe(project_id)
    ap = next((a for a in app.approvals if a.sceneId == scene_id), None)
    if ap is None:
        raise ValueError(f"分镜 {scene_id} 尚未选中任何候选，无法确认")
    if ap.approvalStatus == ApprovalStatus.APPROVED.value and ap.locked:
        # 幂等：已确认
        return app
    if not ap.selectedTemplateId:
        raise ValueError(f"分镜 {scene_id} 未选中模板，无法确认")
    ap.approvalStatus = ApprovalStatus.APPROVED.value
    ap.approvedAt = now_iso()
    ap.locked = True
    return _save_approvals(app)


def revoke_approval(project_id: str, scene_id: str) -> Approvals:
    """撤销确认：APPROVED -> SELECTED（解锁）。"""
    app = read_approvals_safe(project_id)
    ap = next((a for a in app.approvals if a.sceneId == scene_id), None)
    if ap is None:
        raise ValueError(f"分镜 {scene_id} 无审核记录")
    ap.locked = False
    if ap.selectedTemplateId:
        ap.approvalStatus = ApprovalStatus.SELECTED.value
    else:
        ap.approvalStatus = ApprovalStatus.PENDING.value
    ap.approvedAt = ""
    return _save_approvals(app)


def set_modification_notes(project_id: str, scene_id: str, notes: str) -> Approvals:
    app = read_approvals_safe(project_id)
    ap = next((a for a in app.approvals if a.sceneId == scene_id), None)
    if ap is None:
        ap = SceneApproval(sceneId=scene_id)
        app.approvals.append(ap)
    ap.modificationNotes = notes
    return _save_approvals(app)


def request_reselect(project_id: str, scene_id: str, notes: str = "") -> Approvals:
    """要求重新推荐：解锁 + 标记 RECOMMEND_AGAIN。这是允许 Codex 覆盖的唯一途径。"""
    app = read_approvals_safe(project_id)
    ap = next((a for a in app.approvals if a.sceneId == scene_id), None)
    if ap is None:
        ap = SceneApproval(sceneId=scene_id)
        app.approvals.append(ap)
    ap.locked = False  # 解锁，允许 Codex 重写
    ap.approvalStatus = ApprovalStatus.RECOMMEND_AGAIN.value
    ap.approvedAt = ""
    if notes:
        ap.modificationNotes = notes
    return _save_approvals(app)


def mark_no_motion(project_id: str, scene_id: str) -> Approvals:
    """无需动效。"""
    app = read_approvals_safe(project_id)
    ap = next((a for a in app.approvals if a.sceneId == scene_id), None)
    if ap is None:
        ap = SceneApproval(sceneId=scene_id)
        app.approvals.append(ap)
    ap.approvalStatus = ApprovalStatus.NO_MOTION.value
    ap.selectedTemplateId = ""
    ap.selectedTemplateVersion = ""
    ap.locked = True
    ap.approvedAt = now_iso()
    return _save_approvals(app)


# ---------------------------------------------------------------------------
# 状态摘要
# ---------------------------------------------------------------------------


def project_status(project_id: str) -> dict[str, Any]:
    """综合状态，供 CLI status 与 Web 展示。"""
    pd = project_dir(project_id)
    has_sb = storyboard_path(project_id).exists()
    has_rec = recommendations_path(project_id).exists()
    has_app = approvals_path(project_id).exists()
    sb_rev = 0
    rec_rev = 0
    n_scenes = 0
    n_candidates = 0
    n_approved = 0
    n_selected = 0
    n_pending = 0
    n_reselect = 0
    n_no_motion = 0
    if has_sb:
        sb = read_storyboard(project_id)
        sb_rev = sb.projectRevision
        n_scenes = len(sb.scenes)
    if has_rec:
        rec = read_recommendations(project_id)
        rec_rev = rec.recommendationRevision
        for sr in rec.scenes:
            n_candidates += len(sr.candidates)
    if has_sb:
        app = read_approvals_safe(project_id)
        by_id = {a.sceneId: a for a in app.approvals}
        for scene in sb.scenes:
            approval = by_id.get(scene.sceneId)
            state = approval.approvalStatus if approval else ApprovalStatus.PENDING.value
            if state == ApprovalStatus.APPROVED.value and approval.locked:
                n_approved += 1
            elif state == ApprovalStatus.NO_MOTION.value and approval.locked:
                n_no_motion += 1
            elif state == ApprovalStatus.SELECTED.value:
                n_selected += 1
            elif state == ApprovalStatus.RECOMMEND_AGAIN.value:
                n_reselect += 1
            else:
                n_pending += 1
    # 预览产物
    pv = previews_dir(project_id)
    previews = sorted([f.name for f in pv.glob("*.mp4")]) if pv.exists() else []
    od = output_dir(project_id)
    outputs = sorted([f.name for f in od.glob("*.mp4")]) if od.exists() else []
    all_confirmed = (
        has_app
        and n_scenes > 0
        and (n_approved + n_no_motion) == n_scenes
    )
    return {
        "projectId": project_id,
        "projectDir": str(pd),
        "hasStoryboard": has_sb,
        "storyboardRevision": sb_rev,
        "hasRecommendations": has_rec,
        "recommendationRevision": rec_rev,
        "hasApprovals": has_app,
        "sceneCount": n_scenes,
        "candidateCount": n_candidates,
        "approvedCount": n_approved,
        "selectedCount": n_selected,
        "pendingCount": n_pending,
        "reselectCount": n_reselect,
        "noMotionCount": n_no_motion,
        "allConfirmed": all_confirmed,
        "previews": previews,
        "outputs": outputs,
    }


def validate_project(project_id: str) -> dict[str, Any]:
    """校验项目数据一致性。返回 errors/warnings。"""
    errors: list[str] = []
    warnings: list[str] = []
    pd = project_dir(project_id)
    if not pd.exists():
        errors.append(f"项目目录不存在: {pd}")
        return {"valid": False, "errors": errors, "warnings": warnings}
    # storyboard
    try:
        sb = read_storyboard(project_id)
    except FileNotFoundError:
        errors.append("storyboard.json 不存在")
        sb = None
    except Exception as e:  # noqa: BLE001
        errors.append(f"storyboard.json 解析失败: {e}")
        sb = None
    # recommendations
    try:
        rec = read_recommendations(project_id)
    except FileNotFoundError:
        warnings.append("recommendations.json 不存在（Codex 尚未推荐）")
        rec = None
    except Exception as e:  # noqa: BLE001
        errors.append(f"recommendations.json 解析失败: {e}")
        rec = None
    # approvals
    try:
        app = read_approvals(project_id)
    except FileNotFoundError:
        app = None
        warnings.append("approvals.json 不存在（用户尚未审核）")
    except Exception as e:  # noqa: BLE001
        errors.append(f"approvals.json 解析失败: {e}")
        app = None

    if sb and rec:
        sb_ids = {s.sceneId for s in sb.scenes}
        rec_ids = {s.sceneId for s in rec.scenes}
        missing = sb_ids - rec_ids
        if missing:
            warnings.append(f"以下分镜无推荐: {sorted(missing)}")
        if rec.basedOnStoryboardRevision != sb.projectRevision:
            warnings.append(
                f"推荐基于 storyboard rev {rec.basedOnStoryboardRevision}，"
                f"当前 storyboard rev {sb.projectRevision}（可能过时）"
            )
    if rec:
        # 校验候选 previewPath 真实存在（路径相对于 motion-studio 根）
        root = projects_root().parent
        for sr in rec.scenes:
            for c in sr.candidates:
                p = root / c.previewPath if not Path(c.previewPath).is_absolute() else Path(c.previewPath)
                if not p.exists():
                    errors.append(
                        f"分镜 {sr.sceneId} 候选 {c.templateId} 的 previewPath 不存在: {p}"
                    )
    if sb and app:
        sb_ids = {s.sceneId for s in sb.scenes}
        app_ids = {a.sceneId for a in app.approvals}
        extra = app_ids - sb_ids
        if extra:
            warnings.append(f"approvals 含未知分镜: {sorted(extra)}")
        # 校验 SELECTED/APPROVED 的模板在推荐中存在且版本匹配
        if rec:
            for a in app.approvals:
                if a.sceneId not in sb_ids:
                    continue
                if a.approvalStatus in (ApprovalStatus.SELECTED.value, ApprovalStatus.APPROVED.value):
                    sr = next((r for r in rec.scenes if r.sceneId == a.sceneId), None)
                    if sr is None:
                        errors.append(f"分镜 {a.sceneId} 已选中但无推荐记录")
                        continue
                    found = any(c.templateId == a.selectedTemplateId for c in sr.candidates)
                    if not found:
                        warnings.append(
                            f"分镜 {a.sceneId} 选中的模板 {a.selectedTemplateId} "
                            f"不在当前推荐候选中（推荐 rev {a.basedOnRecommendationRevision} vs {rec.recommendationRevision}）"
                        )
    if sb:
        # 时间区间校验
        for s in sb.scenes:
            if s.endMs <= s.startMs:
                errors.append(f"分镜 {s.sceneId} 时间区间无效: {s.startMs}-{s.endMs}")
    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}


def bind_scene_asset(project_id: str, scene_id: str, asset_id: str, scope: str,
                     expected_revision: int, role: str = "background") -> Storyboard:
    """Bind a registered local image or clear media; reject locked scenes and stale revisions.

    Updates storyboard revision atomically. Only this project's or shared assets are accepted.
    """
    from . import library as lib
    from ..models import SceneAssetRef
    sb = read_storyboard(project_id)
    if sb.projectRevision != expected_revision:
        raise ValueError("分镜已更新，请刷新后再绑定素材")
    app = read_approvals_safe(project_id)
    if any(a.sceneId == scene_id and a.locked for a in app.approvals):
        raise PermissionError("分镜已确认，请先撤销确认再修改素材")
    scene = next((s for s in sb.scenes if s.sceneId == scene_id), None)
    if scene is None:
        raise ValueError("分镜不存在")
    if scope not in ("library", project_id) or role != "background":
        raise ValueError("仅支持当前项目或公共库的背景图片")
    refs = [a for a in scene.assets if a.role != role]
    if asset_id:
        asset = next((a for a in lib.load_asset_registry(scope) if a.assetId == asset_id), None)
        if asset is None or asset.mediaType != "image":
            raise ValueError("请选择已登记的图片素材")
        root = lib.assets_dir() if scope == "library" else assets_dir_project(project_id)
        path = (root / asset.localPath).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file():
            raise ValueError("素材路径无效或文件缺失")
        refs.append(SceneAssetRef(role=role, assetId=asset_id,
                    localPath=path.relative_to(lib.library_root().parent).as_posix(), description=asset.name))
    scene.assets = refs
    sb.projectRevision += 1
    write_storyboard(sb)
    return sb


def review_brief(project_id: str) -> dict[str, Any]:
    """Return a read-only AI continuation packet combining current scenes, feedback and candidates.

    This is an explicit file handoff, never an invocation of a model or desktop chat.
    """
    sb = read_storyboard(project_id)
    approvals = read_approvals_safe(project_id)
    try:
        recs = read_recommendations(project_id)
    except FileNotFoundError:
        recs = None
    from . import library as lib
    rows = []
    issues = []
    for scene in sb.scenes:
        ap = next((a for a in approvals.approvals if a.sceneId == scene.sceneId), None)
        rec = next((r for r in recs.scenes if r.sceneId == scene.sceneId), None) if recs else None
        candidates = [c.model_dump() for c in rec.candidates] if rec else []
        state = ap.approvalStatus if ap else "PENDING"
        if state == "APPROVED":
            chosen = next((c for c in candidates if c["templateId"] == ap.selectedTemplateId and c["templateVersion"] == ap.selectedTemplateVersion), None)
            meta = lib.get_template(ap.selectedTemplateId)
            if not chosen or not meta or meta.version != ap.selectedTemplateVersion:
                issues.append({"sceneId":scene.sceneId,"reason":"Confirmed template or candidate version is missing or changed; request explicit reselection"})
        rows.append({**scene.model_dump(), "approvalStatus":state,
                     "locked":ap.locked if ap else False,
                     "selectedTemplateId":ap.selectedTemplateId if ap else "",
                     "selectedTemplateVersion":ap.selectedTemplateVersion if ap else "",
                     "modificationNotes":ap.modificationNotes if ap else "",
                     "basedOnRecommendationRevision":ap.basedOnRecommendationRevision if ap else 0,
                     "candidates":candidates})
    status = project_status(project_id)
    stale = bool(recs and recs.basedOnStoryboardRevision != sb.projectRevision)
    if any(r["approvalStatus"] == "RECOMMEND_AGAIN" for r in rows):
        action = "RECOMMEND_AGAIN"
    elif issues or stale:
        action = "RESOLVE_CONFLICTS"
    elif status["allConfirmed"]:
        action = "GENERATE_SCENE_PREVIEWS"
    else:
        action = "WAIT_FOR_REVIEW"
    import json
    output_reviews_path = project_dir(project_id) / "output-reviews.json"
    output_reviews = json.loads(output_reviews_path.read_text(encoding="utf-8-sig")) if output_reviews_path.exists() else {"reviews":[]}
    return {"sceneEdits":read_scene_edits(project_id),"outputReviews":output_reviews["reviews"],"projectId":project_id,"storyboardRevision":sb.projectRevision,
            "recommendationRevision":recs.recommendationRevision if recs else 0,
            "recommendationsStale":stale,"nextAction":action,
            "allConfirmed":status["allConfirmed"],"issues":issues,"scenes":rows,
            "workbenchPath":f"/#/review/{project_id}",
            "instruction":"AI reads this packet in the current conversation. Preserve locked choices. Workbench never starts AI or production."}


def read_scene_edits(project_id: str) -> dict[str, Any]:
    """Read editor overrides without modifying AI planning or user approvals."""
    from ..models.scene_edits import SceneEdits
    path=project_dir(project_id)/"scene-edits.json"
    return (read_json_model(path,SceneEdits) if path.exists() else SceneEdits()).model_dump()


import threading
_SCENE_EDIT_LOCK = threading.RLock()


def save_scene_edit(project_id: str, scene_id: str, edit: dict, expected_revision: int) -> dict:
    """Serialize workbench editor writes so concurrent tabs cannot pass the same revision check."""
    with _SCENE_EDIT_LOCK:
        return _save_scene_edit_locked(project_id, scene_id, edit, expected_revision)


def _save_scene_edit_locked(project_id: str, scene_id: str, edit: dict, expected_revision: int) -> dict:
    """Save validated visual overrides; reject locked scenes, stale versions and out-of-scene timing."""
    from ..models.scene_edits import SceneEdits,SceneEdit
    from . import library as lib
    storyboard=read_storyboard(project_id)
    scene=next((s for s in storyboard.scenes if s.sceneId==scene_id),None)
    if not scene:raise ValueError("分镜不存在")
    if any(a.sceneId==scene_id and a.locked for a in read_approvals_safe(project_id).approvals):
        raise PermissionError("分镜已确认，请先撤销确认后再编辑")
    saved=SceneEdits.model_validate(read_scene_edits(project_id))
    if saved.revision!=expected_revision:raise ValueError("编辑版本已变化，请重新载入后再保存")
    item=SceneEdit.model_validate(edit)
    meta=lib.get_template(item.templateId)
    if not meta or meta.status!="APPROVED" or meta.version!=item.templateVersion:
        raise ValueError("模板不存在、未通过验证或版本已变化")
    if item.endMs>scene.endMs-scene.startMs:raise ValueError("动效不能超出当前分镜时长")
    allowed={p.name for p in meta.params}|{"styleId"}
    if set(item.props)-allowed:raise ValueError("存在模板未声明的参数")
    if item.layout.transparent and item.templateId not in {"TEXT-001","FLOW-001","COMP-001","DATA-001","NUMBER-001","STICKER-001"}:
        raise ValueError("此模板暂不支持透明前景")
    import math
    for parameter in meta.params:
        if parameter.name not in item.props:
            continue
        value=item.props[parameter.name]
        array=parameter.type=="array" or isinstance(parameter.default,list) or parameter.name in ("nodes","steps")
        if array:
            if not isinstance(value,list) or len(value)>100:raise ValueError(f"{parameter.label} 必须是列表，最多100项")
            if parameter.name=="cueFrames":
                if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<0 for v in value):raise ValueError("节点时间必须是非负数")
            elif any(not isinstance(v,str) or len(v)>5000 for v in value):raise ValueError(f"{parameter.label} 必须使用文本条目")
            if parameter.name=="srcs" and any(v.startswith(("http:","https:","/","\\")) or ".." in v.split("/") for v in value):raise ValueError("素材必须使用本地 public 相对路径")
        elif parameter.type=="number":
            if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):raise ValueError(f"{parameter.label} 必须是数字")
            if parameter.min is not None and value<parameter.min:raise ValueError(f"{parameter.label} 小于允许范围")
            if parameter.max is not None and value>parameter.max:raise ValueError(f"{parameter.label} 超出允许范围")
        elif parameter.type=="boolean":
            if not isinstance(value,bool):raise ValueError(f"{parameter.label} 必须为开关值")
        elif not isinstance(value,str) or len(value)>5000:raise ValueError(f"{parameter.label} 必须为文本")
    if item.templateId.startswith("PRESENTER-"):
        if item.startMs!=0 or item.endMs!=scene.endMs-scene.startMs or item.layout.x!=0 or item.layout.y!=0 or item.layout.scale!=1:
            raise ValueError("真人转场必须连续覆盖整段；请使用人物小窗参数调整位置和大小")
        if item.templateId=="PRESENTER-OUT" and item.props.get("transitionAt",60)<24:
            raise ValueError("回到真人需先预留24帧收起卡片")
        raw=item.props.get("presenterSrc","")
        if raw:
            allowed_root=lib.library_root().parent.resolve()
            path=(allowed_root/raw).resolve()
            if not raw.startswith((f"projects/{project_id}/assets/","library/assets/")) or not path.is_relative_to(allowed_root) or not path.is_file() or path.suffix.lower() not in (".mp4",".mov",".webm",".mkv"):
                raise ValueError("请选择当前项目或公共素材库的真实口播视频")
        if item.props.get("transitionAt",30 if item.templateId=="PRESENTER-IN" else 60)+item.props.get("transitionFrames",26)>(item.endMs-item.startMs)*.03-1:
            raise ValueError("真人转场超出当前动效区间，请调整转场开始帧")
    saved.scenes[scene_id]=item
    saved.revision+=1
    saved.updatedAt=now_iso()
    atomic_write_json(project_dir(project_id)/"scene-edits.json",saved)
    return saved.model_dump()
