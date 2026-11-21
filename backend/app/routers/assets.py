# Author: Codex | Modified: 2026-11-21 16:00:00 +08:00 | Scoped asset folders and safe filenames.
"""素材路由：导入、浏览、分类、校验。"""

from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from ..models import AssetRecord, now_iso
from ..services import library as lib
from ..services import projects as proj

router = APIRouter()


ALLOWED_EXT = {
    "image": {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"},
    "video": {".mp4", ".webm", ".mov", ".mkv"},
    "recording": {".mp4", ".webm", ".mov"},
    "audio": {".mp3", ".wav", ".aac", ".ogg", ".m4a"},
    "icon": {".svg", ".png"},
    "other": {".json", ".txt", ".md"},
}

MAX_SIZE = 200 * 1024 * 1024  # 200MB


def _detect_media_type(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    for mtype, exts in ALLOWED_EXT.items():
        if ext in exts:
            return mtype
    return "other"


@router.get("")
def list_assets(scope: str = "library"):
    """List shared or existing project assets after validating scope."""
    _validate_scope(scope)
    records = lib.load_asset_registry(scope)
    return {"count": len(records), "assets": [r.model_dump() for r in records]}


@router.post("/import")
async def import_asset(
    file: UploadFile = File(...),
    scope: str = Form("library"),
    tags: str = Form(""),
    source: str = Form(""),
    license: str = Form(""),
):
    """上传导入素材。校验类型与大小。"""
    _validate_scope(scope)
    if not file.filename:
        raise HTTPException(400, "缺少文件名")
    if Path(file.filename).name != file.filename or any(c in file.filename for c in ("/", "\\", ":")):
        raise HTTPException(400, "文件名不能包含路径")
    ext = Path(file.filename).suffix.lower()
    media_type = _detect_media_type(file.filename)
    # 校验扩展名
    allowed = set().union(*ALLOWED_EXT.values())
    if ext not in allowed:
        raise HTTPException(400, f"不支持的文件类型: {ext}")

    # 读取并校验大小
    content = await file.read(MAX_SIZE + 1)
    if len(content) > MAX_SIZE:
        raise HTTPException(400, f"文件过大: {len(content)} bytes > {MAX_SIZE}")

    # 确定目标目录
    if scope == "library":
        target_dir = lib.assets_dir()
    else:
        if not proj.project_exists(scope):
            raise HTTPException(404, f"项目不存在: {scope}")
        target_dir = proj.assets_dir_project(scope)

    target_dir.mkdir(parents=True, exist_ok=True)
    # 防止重名：加 uuid 前缀
    safe_name = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    target_path = target_dir / safe_name
    target_path.write_bytes(content)

    # 生成预览路径（图片即自身，视频用 poster 待生成，这里先留空）
    preview = ""
    if media_type == "image":
        preview = safe_name
    elif media_type in ("video", "recording"):
        # 用 ffmpeg 抽第一帧作为 poster
        poster_name = Path(safe_name).stem + "_poster.jpg"
        poster_path = target_dir / poster_name
        import subprocess

        subprocess.run(
            ["ffmpeg", "-y", "-i", str(target_path), "-frames:v", "1", "-q:v", "2", str(poster_path)],
            capture_output=True,
        )
        if poster_path.exists():
            preview = poster_name

    record = AssetRecord(
        assetId=uuid.uuid4().hex[:12],
        name=file.filename,
        mediaType=media_type,
        localPath=safe_name,
        previewPath=preview,
        tags=[t.strip() for t in tags.split(",") if t.strip()],
        source=source,
        license=license,
        fileSizeBytes=len(content),
        createdAt=now_iso(),
    )
    records = lib.load_asset_registry(scope)
    records.append(record)
    lib.save_asset_registry(records, scope)
    return {"ok": True, "asset": record.model_dump()}


@router.delete("/{asset_id}")
def delete_asset(asset_id: str, scope: str = "library"):
    """Delete a scoped asset unless it is still referenced by a storyboard."""
    _validate_scope(scope)
    for pid in proj.list_projects():
        for scene in proj.read_storyboard(pid).scenes:
            if any(a.assetId == asset_id for a in scene.assets):
                raise HTTPException(409, "素材正在被分镜使用，请先解除绑定")
    records = lib.load_asset_registry(scope)
    new_records = []
    deleted = None
    for r in records:
        if r.assetId == asset_id:
            deleted = r
            # 删除文件
            if scope == "library":
                fp = lib.assets_dir() / r.localPath
            else:
                fp = proj.assets_dir_project(scope) / r.localPath
            if fp.exists():
                fp.unlink()
            if r.previewPath:
                pp = fp.parent / r.previewPath
                if pp.exists():
                    pp.unlink()
        else:
            new_records.append(r)
    if not deleted:
        raise HTTPException(404, "素材不存在")
    lib.save_asset_registry(new_records, scope)
    return {"ok": True, "deleted": deleted.assetId}


def _validate_scope(scope: str) -> None:
    """Reject path-like scopes and unknown project folders before reading or writing."""
    if scope == "library":
        return
    if not scope or scope in (".", "..") or any(c in scope for c in ("/", "\\", ":")):
        raise HTTPException(400, "无效的项目素材目录")
    if scope not in proj.list_projects():
        raise HTTPException(404, "项目不存在")
