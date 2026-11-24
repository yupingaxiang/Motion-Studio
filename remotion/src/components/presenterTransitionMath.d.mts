/** Author: Codex | Modified: 2026-11-22 23:59:00 +08:00 | Typed presenter geometry, including persistent episode PiP. */
export function transitionProgress(frame:number,start:number,duration:number):number;
export function presenterRect(frame:number,direction:"in"|"out",start:number,duration:number,pip:{x:number;y:number;width:number;height:number}):{x:number;y:number;width:number;height:number;radius:number};
/** Shrink once and hold the same rectangle until the explicit return frame. */
export function episodePresenterRect(frame:number,enterAt:number,returnAt:number,duration:number,pip:{x:number;y:number;width:number;height:number}):{x:number;y:number;width:number;height:number;radius:number};
/** Resolve spoken card emphasis and its one-shot lift; inactive cards remain still. */
export function presenterCardFocus(frame:number,index:number,cueFrames:number[]):{active:boolean;lift:number};
/** Hold the established PiP when a following teaching scene continues the same presenter. */
export function presenterTemplateRect(frame:number,direction:"in"|"out",start:number,duration:number,pip:{x:number;y:number;width:number;height:number},startInPip?:boolean):{x:number;y:number;width:number;height:number;radius:number};
