import assert from 'node:assert/strict';
import { project, evaluate } from '../src/timeline.js';

// Verify project base contract
assert.equal(project.fps, 24, 'Base FPS must be 24');
assert.equal(project.scenes.length, 42, 'Baseline project contains 42 scenes');
const totalFrames = project.scenes.length * 24; // 1008
const lastValidFrame = totalFrames - 1; // 1007

// 1. Frame 0 (first frame of scene 0)
const f0 = evaluate(0);
assert.equal(f0.frame, 0);
assert.equal(f0.active, 0, 'Frame 0 must activate scene 0');
assert.equal(f0.time, 0);
assert.equal(f0.beat, 0);
assert(typeof f0.wave === 'number');
assert(typeof f0.camera.x === 'number');
assert(typeof f0.camera.y === 'number');
assert(typeof f0.camera.roll === 'number');

// 2. Frame 23 (boundary: last frame of scene 0)
const f23 = evaluate(23);
assert.equal(f23.frame, 23);
assert.equal(f23.active, 0, 'Frame 23 must still be in scene 0');
assert.equal(f23.beat, 23 / 24);

// 3. Frame 24 (boundary: first frame of scene 1)
const f24 = evaluate(24);
assert.equal(f24.frame, 24);
assert.equal(f24.active, 1, 'Frame 24 must switch to scene 1');
assert.equal(f24.time, 1);
assert.equal(f24.beat, 0);

// 4. Frame 47 (boundary: last frame of scene 1)
const f47 = evaluate(47);
assert.equal(f47.frame, 47);
assert.equal(f47.active, 1, 'Frame 47 must still be in scene 1');
assert.equal(f47.beat, 23 / 24);

// 5. Frame 48 (boundary: first frame of scene 2)
const f48 = evaluate(48);
assert.equal(f48.frame, 48);
assert.equal(f48.active, 2, 'Frame 48 must switch to scene 2');
assert.equal(f48.time, 2);
assert.equal(f48.beat, 0);

// 6. Last valid frame: 1007
const fLast = evaluate(lastValidFrame);
assert.equal(fLast.frame, lastValidFrame);
assert.equal(fLast.active, 41, 'Last valid frame must belong to final scene 41');

// 7. Negative frames throw RangeError
assert.throws(() => evaluate(-1), RangeError, 'Negative frame -1 must throw RangeError');
assert.throws(() => evaluate(-24), RangeError, 'Negative frame -24 must throw RangeError');

// 8. Out-of-range frames throw RangeError
assert.throws(() => evaluate(totalFrames), RangeError, 'Frame 1008 (totalFrames) must throw RangeError');
assert.throws(() => evaluate(totalFrames + 100), RangeError, 'Frame > 1008 must throw RangeError');
assert.throws(() => evaluate(1008), RangeError);
assert.throws(() => evaluate(9999), RangeError);

// Non-integer frames throw RangeError
assert.throws(() => evaluate(1.5), RangeError, 'Float frame 1.5 must throw RangeError');
assert.throws(() => evaluate(NaN), RangeError, 'NaN must throw RangeError');
assert.throws(() => evaluate(Infinity), RangeError, 'Infinity must throw RangeError');

// 9. Determinism test: repeated calls produce identical results (deepEqual)
for (const testFrame of [0, 1, 12, 23, 24, 25, 47, 48, 500, lastValidFrame]) {
  const resultA = evaluate(testFrame);
  const resultB = evaluate(testFrame);
  assert.deepEqual(resultA, resultB, `Determinism check failed on frame ${testFrame}`);
}

// 10. Continuous motion dynamics and smooth transition momentum
const fEnter = evaluate(0);
assert.equal(fEnter.motion.phase, 'enter', 'Frame 0 must be in entrance transition phase');
assert(fEnter.motion.shiftX > 0, 'Entrance must have positive decelerating shift');
assert(fEnter.motion.alpha >= 0.6, 'Entrance alpha must be smoothly ramping');

const fSteady = evaluate(12);
assert.equal(fSteady.motion.phase, 'steady', 'Frame 12 must be in steady showcase phase');
assert.equal(fSteady.motion.shiftX, 0, 'Steady phase panel must be locked in position');
assert.equal(fSteady.motion.alpha, 1.0, 'Steady phase alpha must be full opacity');

const fExit = evaluate(23);
assert.equal(fExit.motion.phase, 'exit', 'Frame 23 must be in exit transition phase');
assert(fExit.motion.shiftX < 0, 'Exit must have forward handoff velocity shift');
assert(fExit.motion.alpha <= 1.0, 'Exit alpha must be gently fading');

console.log('Production timeline evaluator: all 10 test categories passed successfully.');
