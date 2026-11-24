/** Author: Codex | Created: 2026-11-22 00:30:00 +08:00 | Typed deterministic element motion contract. | Modified: 2026-11-23 23:21:31 +08:00 */
export type MotionPreset="none"|"fade-up"|"slide-left"|"slide-right"|"pop-in"|"mask-reveal"|"slow-zoom"|"settle-zoom"|"pulse"|"keyframes";
export interface ElementAnimation{preset:MotionPreset;startMs?:number;durationMs?:number;easing?:"smooth"|"ease-out"|"linear"|"back-out";distance?:number;fromScale?:number|null;toScale?:number|null;fromX?:number;fromY?:number;toX?:number;toY?:number}
export type SceneDepth=Record<string,"near"|"middle"|"far">;
export type FocusCue={atMs:number;target:string|null};
export const MOTION_PRESETS:{id:MotionPreset;label:string}[];
/** Return the default scale endpoints for the selected preset. */
export function presetScales(preset:MotionPreset):[number,number];
/** Evaluate a seek-safe sample without browser state or wall-clock timing. */
export function motionAt(config?:ElementAnimation,timeMs?:number):{x:number;y:number;scale:number;opacity:number;reveal:number};
/** Emit only additive individual transform and mask properties. */
export function elementMotionCss(offsets?:Record<string,{x:number;y:number}>,animations?:Record<string,ElementAnimation>,timeMs?:number,unit?:number,protectedIds?:string[],depth?:SceneDepth,focusCues?:FocusCue[]):string;
