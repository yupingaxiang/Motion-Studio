"""库管理服务：加载模板元数据、风格、素材登记，提供语义检索。

Codex Skill 与 Web 后端共用此模块。CLI 的 search 子命令也调用它。
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ..models import (
    AssetRecord,
    Catalog,
    CatalogEntry,
    TemplateMeta,
    TemplateStatus,
    StyleSpec,
)


# ---------------------------------------------------------------------------
# 路径约定
# ---------------------------------------------------------------------------


def library_root() -> Path:
    """library 目录绝对路径。"""
    return (Path(__file__).resolve().parents[3]) / "library"


def motions_dir() -> Path:
    return library_root() / "motions"


def styles_dir() -> Path:
    return library_root() / "styles"


def assets_dir() -> Path:
    return library_root() / "assets"


def catalog_path() -> Path:
    return library_root() / "catalog.json"


def projects_root() -> Path:
    return (Path(__file__).resolve().parents[3]) / "projects"


# ---------------------------------------------------------------------------
# 模板加载与检索
# ---------------------------------------------------------------------------


def load_all_templates(include_deprecated: bool = False) -> list[TemplateMeta]:
    """加载所有模板元数据。仅返回 APPROVED（除非 include_deprecated）。"""
    out: list[TemplateMeta] = []
    root = motions_dir()
    if not root.exists():
        return out
    for d in sorted(root.iterdir()):
        if not d.is_dir():
            continue
        meta_file = d / "meta.json"
        if not meta_file.exists():
            continue
        try:
            with meta_file.open("r", encoding="utf-8-sig") as f:
                raw = json.load(f)
            meta = TemplateMeta.model_validate(raw)
        except Exception as e:  # noqa: BLE001
            print(f"[warn] 跳过无效模板 {d.name}: {e}")
            continue
        if not include_deprecated and meta.status != TemplateStatus.APPROVED.value:
            continue
        out.append(meta)
    return out


def get_template(template_id: str) -> TemplateMeta | None:
    for m in load_all_templates(include_deprecated=True):
        if m.templateId == template_id:
            return m
    return None


def template_preview_abs(template_id: str) -> Path | None:
    """返回模板 preview.mp4 的绝对路径，不存在返回 None。"""
    meta = get_template(template_id)
    if not meta:
        return None
    p = motions_dir() / template_id / meta.previewMp4
    return p if p.exists() else None


def template_source_abs(template_id: str) -> Path | None:
    """返回模板组件源码绝对路径。"""
    meta = get_template(template_id)
    if not meta:
        return None
    # 源码在 remotion/src/components/
    root = (Path(__file__).resolve().parents[3])
    candidates = [
        root / "remotion" / "src" / "components" / meta.component,
        root / "remotion" / "src" / "components" / f"{template_id}.tsx",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


# ---------------------------------------------------------------------------
# 语义检索（轻量关键词/标签匹配，无需外部模型）
# ---------------------------------------------------------------------------


def _tokenize(text: str) -> set[str]:
    """简单分词：小写、按非字母数字拆分、去停用词。支持中英文。"""
    if not text:
        return set()
    # 中文字符保留，按字符处理；英文按词处理
    # 先把中文字符序列切出来
    tokens: set[str] = set()
    # 英文词
    for w in re.findall(r"[a-zA-Z][a-zA-Z0-9_-]*", text.lower()):
        if len(w) > 1:
            tokens.add(w)
    # 中文：按非中文字符拆分后，每个连续中文段做 2-gram
    for seg in re.findall(r"[\u4e00-\u9fff]+", text):
        if len(seg) >= 2:
            for i in range(len(seg) - 1):
                tokens.add(seg[i : i + 2])
        tokens.add(seg)
    return tokens


def _score_template(meta: TemplateMeta, query: str) -> float:
    """对单个模板按查询打分。匹配 useCases/tags/name/description。"""
    if not query.strip():
        return 0.5
    q_tokens = _tokenize(query)
    if not q_tokens:
        return 0.5
    # 模板文本池
    pool_text = " ".join(
        [
            meta.name,
            meta.description,
            meta.category,
            " ".join(meta.useCases),
            " ".join(meta.notUseCases),
            " ".join(meta.tags),
            " ".join(meta.requiredAssets),
        ]
    )
    pool_tokens = _tokenize(pool_text)
    if not pool_tokens:
        return 0.0
    overlap = q_tokens & pool_tokens
    # 加权：useCases/tag 匹配权重更高
    uc_tokens = _tokenize(" ".join(meta.useCases + meta.tags))
    uc_overlap = q_tokens & uc_tokens
    base = len(overlap) / max(len(q_tokens), 1)
    bonus = 0.3 * len(uc_overlap) / max(len(q_tokens), 1)
    score = min(1.0, base + bonus)
    # 不适用场景惩罚
    not_tokens = _tokenize(" ".join(meta.notUseCases))
    if q_tokens & not_tokens:
        score *= 0.6
    return score


def search_templates(
    query: str,
    *,
    category: str | None = None,
    aspect_ratio: str | None = None,
    tags: list[str] | None = None,
    require_assets: list[str] | None = None,
    limit: int = 10,
) -> list[tuple[TemplateMeta, float]]:
    """语义检索模板。返回 (meta, score) 列表，按分数降序。

    仅 APPROVED 模板参与（正式候选推荐要求）。
    """
    templates = load_all_templates(include_deprecated=False)
    results: list[tuple[TemplateMeta, float]] = []
    for m in templates:
        # 硬过滤
        if category and m.category.upper() != category.upper():
            continue
        if aspect_ratio:
            ar_vals = [a if isinstance(a, str) else str(a) for a in m.aspectRatios]
            if aspect_ratio not in ar_vals:
                continue
        if tags:
            m_tags_lower = {t.lower() for t in m.tags}
            if not all(t.lower() in m_tags_lower for t in tags):
                continue
        if require_assets:
            m_req_lower = {r.lower() for r in m.requiredAssets}
            if not all(r.lower() in m_req_lower for r in require_assets):
                continue
        score = _score_template(m, query)
        results.append((m, score))
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:limit]


# ---------------------------------------------------------------------------
# 风格加载
# ---------------------------------------------------------------------------


def load_all_styles() -> list[StyleSpec]:
    out: list[StyleSpec] = []
    root = styles_dir()
    if not root.exists():
        return out
    for d in sorted(root.iterdir()):
        if not d.is_dir():
            continue
        sf = d / "style.json"
        if not sf.exists():
            continue
        try:
            with sf.open("r", encoding="utf-8-sig") as f:
                raw = json.load(f)
            out.append(StyleSpec.model_validate(raw))
        except Exception as e:  # noqa: BLE001
            print(f"[warn] 跳过无效风格 {d.name}: {e}")
    return out


def get_style(style_id: str) -> StyleSpec | None:
    for s in load_all_styles():
        if s.styleId == style_id:
            return s
    return None


def search_styles(query: str, limit: int = 5) -> list[tuple[StyleSpec, float]]:
    styles = load_all_styles()
    results: list[tuple[StyleSpec, float]] = []
    q_tokens = _tokenize(query)
    for s in styles:
        if not query.strip():
            results.append((s, 0.5))
            continue
        pool = " ".join(
            [s.name, s.description, " ".join(s.recommendedScenes), " ".join(s.tags)]
        )
        pt = _tokenize(pool)
        overlap = q_tokens & pt
        results.append((s, len(overlap) / max(len(q_tokens), 1) if q_tokens else 0.5))
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:limit]


# ---------------------------------------------------------------------------
# 素材登记
# ---------------------------------------------------------------------------


def load_asset_registry(scope: str = "library") -> list[AssetRecord]:
    """加载素材登记表。scope=library 读 library/assets/registry.json；
    scope=项目名 读 projects/<scope>/assets/registry.json。"""
    if scope == "library":
        p = assets_dir() / "registry.json"
    else:
        p = projects_root() / scope / "assets" / "registry.json"
    if not p.exists():
        return []
    try:
        with p.open("r", encoding="utf-8-sig") as f:
            raw = json.load(f)
        return [AssetRecord.model_validate(a) for a in raw.get("assets", [])]
    except Exception:  # noqa: BLE001
        return []


def save_asset_registry(records: list[AssetRecord], scope: str = "library") -> None:
    if scope == "library":
        p = assets_dir() / "registry.json"
    else:
        p = projects_root() / scope / "assets" / "registry.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    data = {"assets": [r.model_dump() for r in records]}
    tmp = p.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    import os

    os.replace(tmp, p)


# ---------------------------------------------------------------------------
# catalog.json 生成
# ---------------------------------------------------------------------------


def build_catalog() -> Catalog:
    """扫描 motions + styles，生成 catalog.json。"""
    templates = load_all_templates(include_deprecated=True)
    entries: list[CatalogEntry] = []
    for m in templates:
        ar_vals = [a if isinstance(a, str) else str(a) for a in m.aspectRatios]
        entries.append(
            CatalogEntry(
                templateId=m.templateId,
                name=m.name,
                version=m.version,
                status=m.status,
                category=m.category,
                previewMp4=m.previewMp4,
                posterJpg=m.posterJpg,
                sourceAvailable=m.sourceAvailable,
                useCases=m.useCases,
                tags=m.tags,
                aspectRatios=ar_vals,
                durationFrames=m.durationFrames,
                requiredAssets=m.requiredAssets,
            )
        )
    styles = load_all_styles()
    style_summaries = [
        {
            "styleId": s.styleId,
            "name": s.name,
            "description": s.description,
            "tags": s.tags,
            "recommendedScenes": s.recommendedScenes,
            "exampleImage": s.exampleImage,
        }
        for s in styles
    ]
    from ..models import now_iso

    return Catalog(
        schemaVersion="1.0.0",
        generatedAt=now_iso(),
        templates=entries,
        styles=style_summaries,
    )


def write_catalog() -> Path:
    """生成并写入 catalog.json，返回路径。"""
    cat = build_catalog()
    p = catalog_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    from ..models import atomic_write_json

    atomic_write_json(p, cat)
    return p


def load_catalog() -> Catalog:
    p = catalog_path()
    if not p.exists():
        return build_catalog()
    try:
        with p.open("r", encoding="utf-8-sig") as f:
            raw = json.load(f)
        return Catalog.model_validate(raw)
    except Exception:  # noqa: BLE001
        return build_catalog()


def catalog_summary() -> dict[str, Any]:
    """供 CLI status 输出的摘要。"""
    cat = load_catalog()
    templates = load_all_templates(include_deprecated=True)
    approved = [t for t in templates if t.status == TemplateStatus.APPROVED.value]
    # 检查 preview.mp4 是否真实存在
    ok_preview = 0
    missing_preview: list[str] = []
    for t in templates:
        mp = motions_dir() / t.templateId / t.previewMp4
        if mp.exists():
            ok_preview += 1
        else:
            missing_preview.append(t.templateId)
    return {
        "totalTemplates": len(templates),
        "approvedTemplates": len(approved),
        "previewOk": ok_preview,
        "previewMissing": missing_preview,
        "totalStyles": len(load_all_styles()),
        "catalogPath": str(catalog_path()),
    }
