"""Author: Codex | Modified: 2026-11-21 23:00:00 +08:00 | Validated per-scene visual overrides for AI/workbench handoff."""
from typing import Any,Annotated
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
class SceneEdit(BaseModel):
    """One editable motion instance with timing relative to its scene."""
    model_config=ConfigDict(extra="forbid")
    templateId:str
    templateVersion:str
    props:dict[str,Any]=Field(default_factory=dict)
    elements:dict[Annotated[str,Field(pattern=r"^[a-z][a-z0-9-]{0,63}$")],ElementOffset]=Field(default_factory=dict,max_length=100)
    startMs:int=Field(default=0,ge=0)
    endMs:int=Field(gt=0)
    layout:LayoutEdit=Field(default_factory=LayoutEdit)
    @model_validator(mode="after")
    def valid_time(self):
        """Reject empty or reversed intervals before saving."""
        if self.endMs<=self.startMs:raise ValueError("消失时间必须晚于出现时间")
        return self
class SceneEdits(BaseModel):
    """Atomic versioned document separate from AI-authored recommendations."""
    revision:int=0
    scenes:dict[str,SceneEdit]=Field(default_factory=dict)
    updatedAt:str=""
