/** Author: Codex | Created: 2026-11-21 23:55:00 +08:00 | Seek-safe shared geometry for paired presenter transitions. */
/** Clamp a quintic smoothstep, giving zero velocity at both ends without overshoot. */
export function transitionProgress(frame,start,duration){const t=Math.max(0,Math.min(1,(frame-start)/Math.max(1,duration)));return t*t*t*(t*(t*6-15)+10)}
/** Interpolate a single presenter rectangle; reversing direction preserves exactly matching endpoints. */
export function presenterRect(frame,direction,start,duration,pip){const p=transitionProgress(frame,start,duration);const k=direction==="in"?p:1-p;return {x:pip.x*k,y:pip.y*k,width:1440+(pip.width-1440)*k,height:1080+(pip.height-1080)*k,radius:24*k}}
