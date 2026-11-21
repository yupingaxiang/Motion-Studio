# Author: Codex | Modified: 2026-11-21 18:00:00 +08:00 | Preserve template provenance in API.
"""库浏览路由：模板、风格、catalog。"""

from __future__ import annotations

from fastapi import APIRouter, Query

from ..services import library as lib

router = APIRouter()


@router.get("/catalog")
def get_catalog():
    cat = lib.load_catalog()
    return cat.model_dump()


@router.get("/templates")
def list_templates(status: str | None = None):
    inc = status != "approved"
    templates = lib.load_all_templates(include_deprecated=inc)
    out = []
    for m in templates:
        if status and m.status != status:
            continue
        preview = lib.template_preview_abs(m.templateId)
        out.append(
            {
                "templateId": m.templateId,
                "name": m.name,
                "version": m.version,
                "status": m.status,
                "category": m.category,
                "description": m.description,
                "previewMp4": str(preview.relative_to(lib.library_root().parent)) if preview else None,
                "previewExists": bool(preview),
                "posterJpg": m.posterJpg,
                "sourceAvailable": m.sourceAvailable,
                "sourceName": m.sourceName,
                "sourceUrl": m.sourceUrl,
                "originalId": m.originalId,
                "adaptation": m.adaptation,
                "useCases": m.useCases,
                "notUseCases": m.notUseCases,
                "aspectRatios": m.aspectRatios,
                "durationFrames": m.durationFrames,
                "requiredAssets": m.requiredAssets,
                "tags": m.tags,
                "params": [p.model_dump() for p in m.params],
            }
        )
    return {"count": len(out), "templates": out}


@router.get("/templates/{template_id}")
def get_template(template_id: str):
    m = lib.get_template(template_id)
    if not m:
        return {"error": "not found"}, 404
    preview = lib.template_preview_abs(template_id)
    return {
        **m.model_dump(),
        "previewMp4Abs": str(preview) if preview else None,
        "previewExists": bool(preview),
    }


@router.get("/templates/search")
def search_templates(
    q: str = Query(""),
    category: str | None = None,
    aspect: str | None = None,
    tags: str | None = None,
    assets: str | None = None,
    limit: int = 10,
):
    results = lib.search_templates(
        q,
        category=category,
        aspect_ratio=aspect,
        tags=tags.split(",") if tags else None,
        require_assets=assets.split(",") if assets else None,
        limit=limit,
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
                "useCases": meta.useCases,
                "durationFrames": meta.durationFrames,
            }
        )
    return {"query": q, "count": len(out), "results": out}


@router.get("/styles")
def list_styles():
    styles = lib.load_all_styles()
    return {
        "count": len(styles),
        "styles": [s.model_dump() for s in styles],
    }


@router.get("/styles/{style_id}")
def get_style(style_id: str):
    s = lib.get_style(style_id)
    if not s:
        return {"error": "not found"}
    return s.model_dump()


@router.get("/summary")
def summary():
    return lib.catalog_summary()
