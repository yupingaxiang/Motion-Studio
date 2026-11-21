/** Author: Codex | Created: 2026-11-21 16:00:00 +08:00 | Bound image background for native scene previews. */
import React from "react";
import {AbsoluteFill,Img,staticFile} from "remotion";
/** Wrap a composition with an explicitly bound background, leaving unbound previews unchanged. */
export function withSceneBackground<P extends object>(Component:React.ComponentType<P>):React.FC<P&{backgroundImage?:string}>{
  /** Render the supplied image over the white canvas and below the template foreground. */
  return function SceneWithBackground(props){return <AbsoluteFill><Component {...props}/>{props.backgroundImage&&<Img src={staticFile(props.backgroundImage)} style={{position:"absolute",inset:0,width:"100%",height:"100%",objectFit:"cover",opacity:.1,pointerEvents:"none",mixBlendMode:"multiply"}}/>}</AbsoluteFill>}
}
