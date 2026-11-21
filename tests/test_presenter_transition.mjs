/** Author: Codex | Created: 2026-11-21 23:55:00 +08:00 | Endpoint and seek-safe presenter geometry regression. */
import assert from "node:assert/strict";
import {presenterRect} from "../remotion/src/components/presenterTransitionMath.mjs";
const pip={x:1104,y:672,width:288,height:360};
assert.deepEqual(presenterRect(0,"in",30,26,pip),{x:0,y:0,width:1440,height:1080,radius:0});
assert.deepEqual(presenterRect(56,"in",30,26,pip),{...pip,radius:24});
assert.deepEqual(presenterRect(30,"out",30,26,pip),{...pip,radius:24});
assert.deepEqual(presenterRect(56,"out",30,26,pip),{x:0,y:0,width:1440,height:1080,radius:0});
const mid=presenterRect(43,"out",30,26,pip);
assert.ok(mid.width>288&&mid.width<1440);
assert.deepEqual(presenterRect(43,"out",30,26,pip),mid);
console.log("6 presenter geometry assertions passed");
