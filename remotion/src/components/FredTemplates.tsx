/** Author: Codex | Modified: 2026-11-21 23:30:00 +08:00 | FredTalk MIT source adapters, native geometry preserved on a 4:3 stage. */
import React from "react";
import {AbsoluteFill,staticFile} from "remotion";
import Highlighter from "./fred/highlighter";
import Stack from "./fred/stack";
import Retype from "./fred/retype";
import Focus from "./fred/focus";
/** Preserve the original 960x540 geometry without stretching; center on native 1440x1080 canvas. */
function Stage({children}:{children:React.ReactNode}){return <AbsoluteFill data-motion-canvas="true" style={{background:"white"}}><div style={{position:"absolute",width:960,height:540,left:0,top:135,transform:"scale(1.5)",transformOrigin:"top left"}}>{children}</div></AbsoluteFill>}
/** Adapt real quote copy while preserving the upstream sweep/dim/lift motion. */
export const FredHighlight:React.FC<{heading?:string;highlight?:string;before?:string;after?:string}>=props=><Stage><Highlighter {...props}/></Stage>;
/** Resolve local public image paths; no remote media or author-private assets are used. */
function imagePaths(srcs?:string[]){return (srcs?.length?srcs:["TEXT-001","FLOW-001","COMP-001","DATA-001","TEXT-001"].map(s=>`fred-examples/${s}.jpg`)).map(s=>staticFile(s))}
/** Show five actual images through the original stacked/fanned/flattened trajectories. */
export const FredStack:React.FC<{title?:string;srcs?:string[]}>=({title="从一叠想法，到五个方向",srcs})=><Stage><Stack title={title} srcs={imagePaths(srcs)}/></Stage>;
/** Correct a phrase with the original typing, backspace and retyping timing. */
export const FredRetype:React.FC<{prefix?:string;first?:string;second?:string}>=props=><Stage><Retype prefix="好的表达，靠的是" first="堆砌信息" second="清晰重点" {...props} accent="#8554e8"/></Stage>;
/** Transfer focus between two real images without changing their original geometry. */
export const FredFocus:React.FC<{labels?:string[];srcs?:string[]}>=({labels=["先看文字","再看关系"],srcs})=><Stage><Focus labels={[labels[0]??"",labels[1]??""]} srcs={[imagePaths(srcs)[0],imagePaths(srcs)[1]]}/></Stage>;
