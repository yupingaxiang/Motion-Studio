# Author: Codex | Modified: 2026-11-21 16:00:00 +08:00 | Scene asset binding API.
"""项目路由：列表、storyboard、recommendations、状态、校验。"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..models import Storyboard
from ..services import projects as proj

router = APIRouter()


@router.get("")
def list_projects():
    ids = proj.list_projects()
    return {"count": len(ids), "projects": [{"projectId": pid, **proj.project_status(pid)} for pid in ids]}


@router.get("/{project_id}")
def get_project(project_id: str):
    if not proj.project_exists(project_id):
        raise HTTPException(404, "项目不存在")
    return proj.project_status(project_id)


@router.get("/{project_id}/storyboard")
def get_storyboard(project_id: str):
    if not proj.project_exists(project_id):
        raise HTTPException(404, "项目不存在")
    try:
        sb = proj.read_storyboard(project_id)
        return sb.model_dump()
    except FileNotFoundError:
        raise HTTPException(404, "storyboard.json 不存在")


@router.get("/{project_id}/recommendations")
def get_recommendations(project_id: str):
    if not proj.project_exists(project_id):
        raise HTTPException(404, "项目不存在")
    try:
        from ..models import read_json_model, Recommendations

        rec = read_json_model(proj.recommendations_path(project_id), Recommendations)
        return rec.model_dump()
    except FileNotFoundError:
        return {"projectId": project_id, "scenes": [], "recommendationRevision": 0}


@router.get("/{project_id}/approvals")
def get_approvals(project_id: str):
    if not proj.project_exists(project_id):
        raise HTTPException(404, "项目不存在")
    app = proj.read_approvals_safe(project_id)
    return app.model_dump()


@router.get("/{project_id}/status")
def get_status(project_id: str):
    if not proj.project_exists(project_id):
        raise HTTPException(404, "项目不存在")
    return proj.project_status(project_id)


@router.get("/{project_id}/validate")
def validate_project(project_id: str):
    if not proj.project_exists(project_id):
        raise HTTPException(404, "项目不存在")
    return proj.validate_project(project_id)


@router.get("/{project_id}/previews")
def list_previews(project_id: str):
    if not proj.project_exists(project_id):
        raise HTTPException(404, "项目不存在")
    pv = proj.previews_dir(project_id)
    out = []
    if pv.exists():
        for f in sorted(pv.glob("*.mp4")):
            poster = f.with_suffix(".jpg")
            out.append(
                {
                    "file": f.name,
                    "mp4": str(f.relative_to(proj.projects_root().parent)),
                    "poster": poster.name if poster.exists() else None,
                    "sizeBytes": f.stat().st_size,
                }
            )
    manifest = pv / "manifest.json"
    manifest_data = []
    if manifest.exists():
        import json

        manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
    return {"count": len(out), "previews": out, "manifest": manifest_data}


class BindAssetRequest(BaseModel):
    """Versioned request referencing a registered image instead of an arbitrary path."""
    assetId: str = ""
    scope: str = "library"
    expectedRevision: int


@router.put("/{project_id}/scenes/{scene_id}/asset")
def bind_asset(project_id: str, scene_id: str, body: BindAssetRequest):
    """Persist a scene background image with lock and revision protection."""
    if not proj.project_exists(project_id):
        raise HTTPException(404, "项目不存在")
    try:
        return proj.bind_scene_asset(project_id, scene_id, body.assetId, body.scope, body.expectedRevision).model_dump()
    except PermissionError as exc:
        raise HTTPException(409, str(exc))
    except ValueError as exc:
        raise HTTPException(409, str(exc))


@router.get("/{project_id}/review-brief")
def get_review_brief(project_id: str):
    """Expose the same read-only continuation packet as the local CLI."""
    if project_id not in proj.list_projects():
        raise HTTPException(404, "项目不存在")
    return proj.review_brief(project_id)


class OutputFeedback(BaseModel):
    """User notes tied to one exact rendered output filename."""
    file: str
    notes: str = ""
    updatedAt: str = ""


class OutputReviews(BaseModel):
    """Persist all output review notes using the existing atomic JSON writer."""
    reviews: list[OutputFeedback] = []


@router.get("/{project_id}/outputs")
def list_outputs(project_id: str):
    """List real MP4 outputs and their saved feedback; never generate a placeholder movie."""
    from ..models import read_json_model
    if project_id not in proj.list_projects():
        raise HTTPException(404, "项目不存在")
    folder = proj.output_dir(project_id)
    review_file = proj.project_dir(project_id) / "output-reviews.json"
    reviews = read_json_model(review_file, OutputReviews).reviews if review_file.exists() else []
    files = sorted(folder.glob("*.mp4"), key=lambda p:p.stat().st_mtime, reverse=True) if folder.exists() else []
    return {"outputs":[{"file":p.name,"path":p.relative_to(proj.projects_root().parent).as_posix(),
             "sizeBytes":p.stat().st_size,
             "notes":next((r.notes for r in reviews if r.file == p.name), "")} for p in files]}


@router.put("/{project_id}/output-review")
def save_output_review(project_id: str, body: OutputFeedback):
    """Save feedback for an existing local MP4 so the AI can read it on continuation."""
    from ..models import atomic_write_json, read_json_model, now_iso
    if project_id not in proj.list_projects():
        raise HTTPException(404, "项目不存在")
    if Path(body.file).name != body.file or any(c in body.file for c in ("/", "\\", ":")):
        raise HTTPException(400, "无效的成片文件名")
    if not body.file.endswith(".mp4") or not (proj.output_dir(project_id) / body.file).is_file():
        raise HTTPException(404, "成片不存在")
    path = proj.project_dir(project_id) / "output-reviews.json"
    saved = read_json_model(path, OutputReviews) if path.exists() else OutputReviews()
    body.updatedAt = now_iso()
    saved.reviews = [r for r in saved.reviews if r.file != body.file] + [body]
    atomic_write_json(path, saved)
    return body.model_dump()
