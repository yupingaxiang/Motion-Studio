/** Author: Codex | Created: 2026-11-21 19:00:00 +08:00 | Types for deterministic frame math. */
/** Calculate the integer value at a frame. */
export function countAt(frame:number,start:number,end:number,frames:number):number;
/** Calculate the media index, or -1 for no media. */
export function cutAt(frame:number,length:number,cutFrames:number,flashFrames:number):number;
