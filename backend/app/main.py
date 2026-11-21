"""FastAPI 后端主应用。

提供 Web 工作台所需的 REST API：
- 项目、分镜、推荐、审核的读写
- 模板库、风格库、素材库的浏览
- 媒体文件（MP4/poster）的静态服务
- 审核操作（select/approve/revoke/reselect/no-motion/notes）—— 含冲突保护
"""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routers import library, projects, approvals, assets

_ROOT = Path(__file__).resolve().parents[2]

app = FastAPI(title="Motion Studio API", version="1.0.0")

# CORS：允许前端 dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由
app.include_router(library.router, prefix="/api/library", tags=["library"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(approvals.router, prefix="/api/approvals", tags=["approvals"])
app.include_router(assets.router, prefix="/api/assets", tags=["assets"])


# 静态媒体服务：library/motions, library/styles, projects
# 让前端能直接访问真实 MP4 与 poster
@app.get("/api/health")
def health():
    return {"status": "ok", "service": "motion-studio-api"}


# 挂载静态目录（媒体文件）
_lib_root = _ROOT / "library"
_proj_root = _ROOT / "projects"
_lib_root.mkdir(parents=True, exist_ok=True)
_proj_root.mkdir(parents=True, exist_ok=True)

app.mount("/media/library", StaticFiles(directory=str(_lib_root)), name="media-library")
app.mount("/media/projects", StaticFiles(directory=str(_proj_root)), name="media-projects")

# 前端构建产物（生产模式）
_web_dist = _ROOT / "frontend" / "dist"
if _web_dist.exists():
    app.mount("/", StaticFiles(directory=str(_web_dist), html=True), name="web")
