"""Author: Codex | Modified: 2026-11-23 23:21:31 +08:00 | Validated per-scene visual overrides for AI/workbench handoff."""
import math
from typing import Any,Annotated,Literal
from pydantic import BaseModel,Field,ConfigDict,model_validator
class LayoutEdit(BaseModel):
    """Whole-card translation/scale and foreground transparency, not arbitrary HTML/CSS."""
    model_config=ConfigDict(extra="forbid")
    x:float=Field(default=0,ge=-1440,le=1440)
    y:float=Field(default=0,ge=-1080,le=1080)
    scale:float=Field(default=1,ge=.1,le=3)
    transparent:bool=False
class ElementOffset(BaseModel):
    """Independent composition-space translation, bounded and finite for safe deterministic rendering."""
    model_config=ConfigDict(extra="forbid")
    x:float=Field(default=0,ge=-1440,le=1440,allow_inf_nan=False)
    y:float=Field(default=0,ge=-1080,le=1080,allow_inf_nan=False)
class ElementAnimation(BaseModel):
    """Seek-safe additive animation parameters, independent of static drag offsets."""
    model_config=ConfigDict(extra="forbid")
    preset:Literal["none","fade-up","slide-left","slide-right","pop-in","mask-reveal","slow-zoom","settle-zoom","pulse","keyframes"]="none"
    startMs:int=Field(default=0,ge=0,le=3600000)
    durationMs:int=Field(default=600,ge=100,le=60000)
    easing:Literal["smooth","ease-out","linear","back-out"]="smooth"
    distance:float=Field(default=60,ge=0,le=1440,allow_inf_nan=False)
    fromScale:float|None=Field(default=None,ge=.1,le=3,allow_inf_nan=False)
    toScale:float|None=Field(default=None,ge=.1,le=3,allow_inf_nan=False)
    fromX:float=Field(default=0,ge=-1440,le=1440,allow_inf_nan=False)
    fromY:float=Field(default=0,ge=-1080,le=1080,allow_inf_nan=False)
    toX:float=Field(default=0,ge=-1440,le=1440,allow_inf_nan=False)
    toY:float=Field(default=0,ge=-1080,le=1080,allow_inf_nan=False)
ElementId=Annotated[str,Field(pattern=r"^[a-z][a-z0-9-]{0,63}$")]
class FocusCue(BaseModel):
    """Start a focus change in scene time; null restores the overview."""
    model_config=ConfigDict(extra="forbid")
    atMs:int=Field(ge=0)
    target:ElementId|None=None
class SceneEdit(BaseModel):
    """One editable motion instance with timing relative to its scene."""
    model_config=ConfigDict(extra="forbid")
    templateId:str
    templateVersion:str
    props:dict[str,Any]=Field(default_factory=dict)
    elements:dict[Annotated[str,Field(pattern=r"^[a-z][a-z0-9-]{0,63}$")],ElementOffset]=Field(default_factory=dict,max_length=100)
    animations:dict[Annotated[str,Field(pattern=r"^[a-z][a-z0-9-]{0,63}$")],ElementAnimation]=Field(default_factory=dict,max_length=100)
    depth:dict[ElementId,Literal["near","middle","far"]]=Field(default_factory=dict,max_length=100)
    focusCues:list[FocusCue]=Field(default_factory=list,max_length=100)
    startMs:int=Field(default=0,ge=0)
    endMs:int=Field(gt=0)
    layout:LayoutEdit=Field(default_factory=LayoutEdit)
    @model_validator(mode="after")
    def valid_time(self):
        """Reject empty or reversed intervals before saving."""
        if self.endMs<=self.startMs:raise ValueError("消失时间必须晚于出现时间")
        if "presenter" in self.depth or any(c.target=="presenter" for c in self.focusCues):
            raise ValueError("人物小窗不参与景深或焦点切换")
        previous=self.startMs-1
        final_frame=(math.ceil(self.endMs*.03) if self.templateId.startswith("PRESENTER-") else math.floor(self.endMs*.03+.5))-1
        for cue in self.focusCues:
            if cue.atMs<=previous or cue.atMs+400>final_frame/30*1000+1e-6:
                raise ValueError("焦点时间须递增，并在动效结束前留出 0.4 秒")
            if cue.target is not None and cue.target not in self.depth:
                raise ValueError("焦点必须指向已分层的元素")
            previous=cue.atMs
        for key,animation in self.animations.items():
            if animation.preset=="none":continue
            if animation.startMs<self.startMs or animation.startMs+animation.durationMs>final_frame/30*1000+1e-6:
                raise ValueError("元素动效必须在当前动效出现区间内完成")
            if self.templateId.startswith("PRESENTER-") and key=="presenter":
                raise ValueError("人物视频请使用专用小窗转场参数，不能叠加会破坏全屏终点的动效")
        return self
class SceneEdits(BaseModel):
    """Atomic versioned document separate from AI-authored recommendations."""
    revision:int=0
    scenes:dict[str,SceneEdit]=Field(default_factory=dict)
    updatedAt:str=""
