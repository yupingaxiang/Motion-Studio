/** Author: Codex | Created: 2026-11-21 19:00:00 +08:00 | Deterministic counter/flash timing regressions. */
import assert from "node:assert/strict";
import {countAt,cutAt} from "../remotion/src/components/counterFlashMath.mjs";
assert.equal(countAt(0,1,20,45),1);
assert.equal(countAt(45,1,20,45),20);
assert.equal(countAt(300,1,20,45),20);
assert.equal(countAt(20,20,1,20),1);
assert.equal(countAt(10,1,20,0),20);
assert.equal(cutAt(0,4,6,45),0);
assert.equal(cutAt(6,4,6,45),1);
assert.equal(cutAt(24,4,6,45),0);
assert.equal(cutAt(90,4,6,45),3);
assert.equal(cutAt(90,0,6,45),-1);
console.log("10 counter and cut timing assertions passed");
