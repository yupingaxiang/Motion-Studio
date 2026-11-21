"""审核路由：select / approve / revoke / reselect / no-motion / notes。

选择与确认是两个独立操作。APPROVED 后锁定，需 reselect 才能解锁。
所有写操作经 projects 服务的冲突保护逻辑。
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services import projects as proj

router = APIRouter()


class SelectReq(BaseModel):
    projectId: str
    sceneId: str
    templateId: str
    templateVersion: str
    basedOnRecommendationRevision: int


class SceneReq(BaseModel):
    projectId: str
    sceneId: str


class NotesReq(BaseModel):
    projectId: str
    sceneId: str
    notes: str


@router.post("/select")
def select(req: SelectReq):
    """选中候选（SELECTED，尚未确认）。"""
    try:
        app = proj.select_candidate(
            req.projectId,
            req.sceneId,
            req.templateId,
            req.templateVersion,
            req.basedOnRecommendationRevision,
        )
        return app.model_dump()
    except PermissionError as e:
        raise HTTPException(409, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/approve")
def approve(req: SceneReq):
    """确认分镜（APPROVED，锁定）。"""
    try:
        app = proj.approve_scene(req.projectId, req.sceneId)
        return app.model_dump()
    except PermissionError as e:
        raise HTTPException(409, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/revoke")
def revoke(req: SceneReq):
    """撤销确认（APPROVED -> SELECTED）。"""
    try:
        app = proj.revoke_approval(req.projectId, req.sceneId)
        return app.model_dump()
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/reselect")
def reselect(req: NotesReq):
    """要求重新推荐（解锁，允许 Codex 覆盖）。"""
    app = proj.request_reselect(req.projectId, req.sceneId, req.notes)
    return app.model_dump()


@router.post("/no-motion")
def no_motion(req: SceneReq):
    """无需动效。"""
    app = proj.mark_no_motion(req.projectId, req.sceneId)
    return app.model_dump()


@router.post("/notes")
def set_notes(req: NotesReq):
    """修改意见。"""
    app = proj.set_modification_notes(req.projectId, req.sceneId, req.notes)
    return app.model_dump()
