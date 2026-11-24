/** Author: Codex | Modified: 2026-11-22 23:59:00 +08:00 | Seek-safe presenter transitions with an explicit persistent episode hold. */
/** Clamp a quintic smoothstep, giving zero velocity at both ends without overshoot. */
export function transitionProgress(frame,start,duration){const t=Math.max(0,Math.min(1,(frame-start)/Math.max(1,duration)));return t*t*t*(t*(t*6-15)+10)}
/** Interpolate a single presenter rectangle; reversing direction preserves exactly matching endpoints. */
export function presenterRect(frame,direction,start,duration,pip){const p=transitionProgress(frame,start,duration);const k=direction==="in"?p:1-p;return {x:pip.x*k,y:pip.y*k,width:1440+(pip.width-1440)*k,height:1080+(pip.height-1080)*k,radius:24*k}}
/** Shrink once, hold across every chapter, and expand only at the explicit return cue. */
export function episodePresenterRect(frame,enterAt,returnAt,duration,pip){return frame<returnAt?presenterRect(frame,"in",enterAt,duration,pip):presenterRect(frame,"out",returnAt,duration,pip)}
/** Continue an established PiP without replaying entry; explicit return templates still expand normally. */
export function presenterTemplateRect(frame,direction,start,duration,pip,startInPip=false){return direction==="in"&&startInPip?{...pip,radius:24}:presenterRect(frame,direction,start,duration,pip)}
/** Select the last spoken point and apply a restrained, single rise-and-settle motion on activation. */
export function presenterCardFocus(frame,index,cueFrames){let current=-1;for(let i=0;i<cueFrames.length;i++)if(frame>=cueFrames[i])current=i;const active=current===index;const elapsed=frame-cueFrames[index];const lift=active&&elapsed>=0&&elapsed<24?12*Math.sin(Math.PI*elapsed/24)*Math.exp(-elapsed/20):0;return {active,lift}}
