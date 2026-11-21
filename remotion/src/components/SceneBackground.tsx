/** Author: Codex | Modified: 2026-11-21 23:30:00 +08:00 | Real bound background beneath reusable template foreground. */
import React from "react";
import {AbsoluteFill,Img,staticFile} from "remotion";
/** Render the full scene background without tinting or intercepting foreground hit testing. */
export function SceneBackgroundLayer({src,children}:{src?:string;children:React.ReactNode}){return <AbsoluteFill className={src?"scene-bound-background":undefined}><style>{`.scene-bound-background [data-motion-canvas]{background:transparent!important}.scene-bound-background [data-motion-paper]{display:none}`}</style>{src&&<Img data-scene-background="true" src={src} style={{position:"absolute",inset:0,width:"100%",height:"100%",objectFit:"cover",pointerEvents:"none"}}/>}{children}</AbsoluteFill>}
/** Keep standalone native template compositions compatible with staged scene images. */
export function withSceneBackground<P extends object>(Component:React.ComponentType<P>):React.FC<P&{backgroundImage?:string}>{
  /** Use the same backdrop and foreground contract as live scene editing. */
  return function SceneWithBackground(props){return <SceneBackgroundLayer src={props.backgroundImage?staticFile(props.backgroundImage):undefined}><Component {...props}/></SceneBackgroundLayer>}
}
