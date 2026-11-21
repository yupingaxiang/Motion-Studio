/** Author: Codex | Modified: 2026-11-21 23:55:00 +08:00 | Shared real-time and export composition for one editable scene card. */
import React from "react";
import {AbsoluteFill,Sequence,Img,staticFile} from "remotion";
import {SceneBackgroundLayer} from "./SceneBackground";
import {PresenterEnter,PresenterReturn} from "./PresenterTransition";
import {TextReveal} from "./TextReveal";
import {FlowExpand} from "./FlowExpand";
import {ConceptCompare} from "./ConceptCompare";
import {DataTrend} from "./DataTrend";
import {NumberCounter,MediaFlash,CounterFlashIntro} from "./CounterFlash";
import {StickerExplainer} from "./StickerExplainer";
import {FredHighlight,FredStack,FredRetype,FredFocus} from "./FredTemplates";
export const EDITABLE_TEMPLATES:Record<string,React.ComponentType<any>>={"PRESENTER-IN":PresenterEnter,"PRESENTER-OUT":PresenterReturn,"TEXT-001":TextReveal,"FLOW-001":FlowExpand,"COMP-001":ConceptCompare,"DATA-001":DataTrend,"NUMBER-001":NumberCounter,"MEDIA-001":MediaFlash,"INTRO-001":CounterFlashIntro,"STICKER-001":StickerExplainer,"FRED-V087":FredHighlight,"FRED-STACK":FredStack,"FRED-RETYPE":FredRetype,"FRED-FOCUS":FredFocus};
export const TRANSPARENT_TEMPLATES=["TEXT-001","FLOW-001","COMP-001","DATA-001","NUMBER-001","STICKER-001"];
export interface SceneLayout{x:number;y:number;scale:number;transparent:boolean}
export type EditableSceneProps = {templateId:string;content:Record<string,any>;layout:SceneLayout;startMs:number;endMs:number;elements?:Record<string,{x:number;y:number}>;sceneDurationMs?:number}
/** Apply one deterministic visual override; the same component is used by Player and scene preview rendering. */
export const EditableScene:React.FC<EditableSceneProps>=({templateId,content,layout,startMs,endMs,elements={},sceneDurationMs})=>{const Component=EDITABLE_TEMPLATES[templateId];if(!Component)return <AbsoluteFill style={{color:"#8554e8",background:"white",justifyContent:"center",alignItems:"center"}}>当前模板没有可用的编辑组件</AbsoluteFill>;const isPresenter=templateId.startsWith("PRESENTER-");const transparent=layout.transparent&&TRANSPARENT_TEMPLATES.includes(templateId);const unit=templateId.startsWith("FRED-")?1.5:1;const elementCss=Object.entries(elements).filter(([id,pos])=>!(templateId.startsWith("PRESENTER-")&&id==="presenter")&&/^[a-z][a-z0-9-]{0,63}$/.test(id)&&Number.isFinite(pos.x)&&Number.isFinite(pos.y)).map(([id,pos])=>`[data-motion-element="${id}"]{translate:${pos.x/unit}px ${pos.y/unit}px}`).join("");const start=isPresenter?0:Math.round(startMs*.03);const end=Math.max(start+1,(isPresenter?Math.ceil((sceneDurationMs??endMs)*.03):Math.round(endMs*.03)));return <SceneBackgroundLayer src={content.backgroundImageUrl??(content.backgroundImage?staticFile(content.backgroundImage):undefined)}><style>{elementCss}</style><style>{`.motion-transparent>div{background:transparent!important}.motion-transparent.sticker>div>svg:first-child{display:none}`}</style><Sequence from={start} durationInFrames={end-start}><div style={{position:"absolute",inset:0,transform:isPresenter?undefined:`translate(${layout.x}px,${layout.y}px) scale(${layout.scale})`,transformOrigin:"center center"}}><div className={transparent?`motion-transparent ${templateId==="STICKER-001"?"sticker":""}`:undefined} style={{position:"absolute",inset:0}}><Component {...content} {...(templateId.startsWith("PRESENTER-")?{presenterOffset:elements.presenter}:{})}/></div></div></Sequence></SceneBackgroundLayer>};
