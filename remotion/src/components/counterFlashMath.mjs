/** Author: Codex | Created: 2026-11-21 19:00:00 +08:00 | Pure seek-safe counting and hard-cut frame selection. */
/** Return an integer count, clamped before/after the reveal; supports ascending and descending ranges. */
export function countAt(frame,start,end,frames){const p=frames<=0?1:Math.max(0,Math.min(1,frame/frames));return Math.round(start+(end-start)*p)}
/** Return the hard-cut media index, then hold the last asset; empty arrays return -1. */
export function cutAt(frame,length,cutFrames,flashFrames){if(length<1)return -1;if(frame>=flashFrames)return length-1;return Math.floor(Math.max(0,frame)/Math.max(1,cutFrames))%length}
