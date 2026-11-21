# Author: Codex | Modified: 2026-11-21 15:30:00 +08:00 | Native 4:3 template protocol.
"""Pydantic 数据协议模型 —— Motion Studio 共享数据契约。

这些模型定义了 Codex（通过 Skill + CLI）与 Web 工作台（通过 FastAPI）之间
共享的结构化数据格式。所有 JSON 文件在写入前都经过这些模型校验。
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# 枚举
# ---------------------------------------------------------------------------


class ApprovalStatus(str, Enum):
    """审核状态。SELECTED 与 APPROVED 必须区分：选中 ≠ 确认。"""

    PENDING = "PENDING"  # Codex 已推荐，用户尚未操作
    SELECTED = "SELECTED"  # 用户选中了某候选，但尚未确认
    APPROVED = "APPROVED"  # 用户确认，模板锁定，不可静默替换
    RECOMMEND_AGAIN = "RECOMMEND_AGAIN"  # 用户要求重新推荐
    NO_MOTION = "NO_MOTION"  # 用户决定该分镜无需动效


class TemplateStatus(str, Enum):
    """模板入库状态。仅 APPROVED 模板参与正式候选推荐。"""

    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    DEPRECATED = "DEPRECATED"


class AspectRatio(str, Enum):
    """Supported native aspect ratios."""
    LANDSCAPE_4_3 = "4:3"
    PORTRAIT_9_16 = "9:16"
    LANDSCAPE_16_9 = "16:9"
    SQUARE_1_1 = "1:1"


# ---------------------------------------------------------------------------
# 动效模板元数据（library/motions/<ID>/meta.json）
# ---------------------------------------------------------------------------


class TemplateParam(BaseModel):
    """单个可配置参数。"""

    name: str
    type: str = Field(description="string | number | boolean | color | select")
    label: str
    default: Any
    required: bool = False
    description: str = ""
    options: Optional[list[str]] = None  # type=select 时使用
    min: Optional[float] = None
    max: Optional[float] = None


class TemplateMeta(BaseModel):
    """单个动效模板的完整元数据。

    与 library/motions/<templateId>/meta.json 一一对应。
    """

    templateId: str
    name: str
    description: str
    version: str = Field(description="语义化版本号，如 1.0.0")
    status: TemplateStatus = TemplateStatus.APPROVED
    component: str = Field(description="Remotion 组件文件名，如 TextReveal.tsx")
    compositionId: str = Field(description="Remotion composition id")

    # 预览产物（模板入库时预渲染）
    previewMp4: str = Field(description="相对 library/motions/<id>/ 的 preview.mp4 路径")
    posterJpg: str = Field(description="相对 library/motions/<id>/ 的 poster.jpg 路径")
    sourceAvailable: bool = True
    sourceName: str = "Motion Studio"
    sourceUrl: str = ""
    originalId: str = ""
    adaptation: str = ""

    # 适用性
    useCases: list[str] = Field(default_factory=list, description="适用场景关键词")
    notUseCases: list[str] = Field(default_factory=list, description="不适用场景关键词")
    aspectRatios: list[AspectRatio] = Field(default_factory=list)
    durationFrames: int = Field(description="默认时长（帧，30fps）")
    minDurationFrames: int = 30
    maxDurationFrames: int = 600

    # 素材需求
    requiredAssets: list[str] = Field(
        default_factory=list,
        description="所需素材类型：image | video | recording | audio | icon",
    )
    optionalAssets: list[str] = Field(default_factory=list)

    # 可配置参数
    params: list[TemplateParam] = Field(default_factory=list)

    # 标签与检索
    tags: list[str] = Field(default_factory=list)
    category: str = Field(description="TEXT | FLOW | COMP | DEMO | DATA | TRANS")

    model_config = ConfigDict(use_enum_values=True)


# ---------------------------------------------------------------------------
# 风格定义（library/styles/<style_id>/style.json）
# ---------------------------------------------------------------------------


class ColorSpec(BaseModel):
    name: str
    hex: str
    usage: str = ""


class StyleSpec(BaseModel):
    """单个视觉风格的完整定义。"""

    styleId: str
    name: str
    description: str

    # 色彩
    colors: list[ColorSpec] = Field(default_factory=list)
    background: str = "#000000"
    foreground: str = "#ffffff"

    # 构图
    compositionRules: list[str] = Field(default_factory=list)

    # 字体
    fontSuggestions: list[str] = Field(default_factory=list)
    titleFont: str = ""
    bodyFont: str = ""

    # 动画节奏
    animationRhythm: list[str] = Field(default_factory=list)

    # 图像生成
    imagePromptTemplate: str = ""
    negativePrompt: str = ""

    # 示例
    exampleImage: str = Field(default="", description="相对 style 目录的示例图路径")
    exampleVideo: str = ""

    # 场景
    recommendedScenes: list[str] = Field(default_factory=list)
    forbiddenScenes: list[str] = Field(default_factory=list)

    tags: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# 素材登记（library/assets / projects/<p>/assets）
# ---------------------------------------------------------------------------


class AssetRecord(BaseModel):
    assetId: str
    name: str
    mediaType: str = Field(description="image | video | recording | audio | icon | other")
    localPath: str
    previewPath: str = ""
    tags: list[str] = Field(default_factory=list)
    source: str = ""
    license: str = ""
    fileSizeBytes: int = 0
    width: int = 0
    height: int = 0
    durationMs: int = 0
    usageCount: int = 0
    createdAt: str = ""


# ---------------------------------------------------------------------------
# 分镜（storyboard.json）
# ---------------------------------------------------------------------------


class SceneAssetRef(BaseModel):
    """分镜引用的素材。"""

    role: str = Field(description="main | background | overlay | icon | audio")
    assetId: str = ""
    localPath: str = ""
    description: str = ""


class Scene(BaseModel):
    sceneId: str
    narration: str
    startMs: int
    endMs: int
    visualIntent: str
    assets: list[SceneAssetRef] = Field(default_factory=list)
    styleId: str = "minimal-tech"


class Storyboard(BaseModel):
    """由 Codex 生成和修改。"""

    projectId: str
    projectRevision: int = 1
    script: str = Field(default="", description="原始口播稿")
    scenes: list[Scene] = Field(default_factory=list)
    updatedAt: str = ""


# ---------------------------------------------------------------------------
# 候选推荐（recommendations.json）—— Codex 写入
# ---------------------------------------------------------------------------


class Candidate(BaseModel):
    """单个候选动效。"""

    templateId: str
    templateVersion: str
    previewPath: str = Field(description="必须指向实际存在的本地 MP4")
    posterPath: str = ""
    recommendationReason: str
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    requiredAssets: list[str] = Field(default_factory=list)
    compatibility: str = Field(default="full", description="full | partial | needs-assets")
    proposedProps: dict[str, Any] = Field(default_factory=dict)

    @field_validator("previewPath")
    @classmethod
    def _preview_not_empty(cls, v: str) -> str:
        if not v:
            raise ValueError("previewPath 不能为空，必须指向真实 MP4")
        return v


class SceneRecommendation(BaseModel):
    sceneId: str
    recommendationRevision: int = 1
    candidates: list[Candidate] = Field(default_factory=list, max_length=3)
    generatedAt: str = ""


class Recommendations(BaseModel):
    """整个项目的推荐集合。"""

    projectId: str
    recommendationRevision: int = 1
    basedOnStoryboardRevision: int = 1
    scenes: list[SceneRecommendation] = Field(default_factory=list)
    updatedAt: str = ""


# ---------------------------------------------------------------------------
# 审核结果（approvals.json）—— Web 工作台写入
# ---------------------------------------------------------------------------


class SceneApproval(BaseModel):
    sceneId: str
    selectedTemplateId: str = Field(default="", description="用户选中的模板，SELECTED 阶段写入")
    selectedTemplateVersion: str = ""
    approvalStatus: ApprovalStatus = ApprovalStatus.PENDING
    modificationNotes: str = ""
    approvedAt: str = ""
    basedOnRecommendationRevision: int = 1
    locked: bool = Field(
        default=False,
        description="APPROVED 后锁定，Codex 重新推荐时不可静默覆盖",
    )

    model_config = ConfigDict(use_enum_values=True)


class Approvals(BaseModel):
    projectId: str
    approvals: list[SceneApproval] = Field(default_factory=list)
    updatedAt: str = ""


# ---------------------------------------------------------------------------
# catalog.json —— 全库索引
# ---------------------------------------------------------------------------


class CatalogEntry(BaseModel):
    """catalog.json 中每个模板的索引项。"""

    templateId: str
    name: str
    version: str
    status: str
    category: str
    previewMp4: str
    posterJpg: str
    sourceAvailable: bool
    useCases: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    aspectRatios: list[str] = Field(default_factory=list)
    durationFrames: int = 0
    requiredAssets: list[str] = Field(default_factory=list)


class Catalog(BaseModel):
    """整个动效库的索引，供 Codex 检索与 Web 展示。"""

    schemaVersion: str = "1.0.0"
    generatedAt: str = ""
    templates: list[CatalogEntry] = Field(default_factory=list)
    styles: list[dict[str, Any]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# 辅助
# ---------------------------------------------------------------------------


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_write_json(path: Path, model: BaseModel) -> None:
    """原子写入 JSON：先写临时文件再重命名，避免 Codex 与 Web 同时写损坏。

    同时写入 _meta 校验文件，包含内容哈希，用于冲突检测。
    """
    import hashlib
    import json
    import os
    import tempfile

    path.parent.mkdir(parents=True, exist_ok=True)
    data = model.model_dump_json(indent=2, exclude_none=True)
    digest = hashlib.sha256(data.encode("utf-8")).hexdigest()

    # 写到同目录临时文件，再原子替换
    fd, tmp = tempfile.mkstemp(
        prefix=path.stem + ".", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise

    # 写哈希元数据（用于乐观并发校验）
    meta_path = path.with_suffix(path.suffix + ".meta")
    meta = {"sha256": digest, "updatedAt": now_iso(), "bytes": len(data.encode("utf-8"))}
    fd2, tmp2 = tempfile.mkstemp(
        prefix=meta_path.stem + ".", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd2, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp2, meta_path)
    except Exception:
        try:
            os.unlink(tmp2)
        except OSError:
            pass


def read_json_model(path: Path, model_cls: type[BaseModel]) -> BaseModel:
    """读取并校验 JSON 文件为指定模型。文件不存在时抛 FileNotFoundError。"""
    import json

    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")
    with path.open("r", encoding="utf-8-sig") as f:
        raw = json.load(f)
    return model_cls.model_validate(raw)
