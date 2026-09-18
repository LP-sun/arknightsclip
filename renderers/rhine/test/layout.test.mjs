import assert from 'node:assert/strict';
import { getStageZones, computePlayerSlotLayout } from '../src/layout.js';

// 1. Stage zones structure
const zones = getStageZones();
assert.equal(zones.canvas.width, 1920);
assert.equal(zones.canvas.height, 1080);
assert(zones.safeArea.width > 1800, 'SafeArea width should exceed 1800px');
assert(zones.safeArea.height > 980, 'SafeArea height should exceed 980px');
assert(zones.header.height > 50, 'Header should have sufficient height');
assert(zones.footer.height > 30, 'Footer should have sufficient height');
assert(zones.content.height > 800, 'Content zone should occupy majority of canvas');

// 2. Horizontal player slots (Hero mode)
const horizontalContainer = { x: 100, y: 800, width: 800, height: 40 };

// 5 players
const slots5H = computePlayerSlotLayout(5, horizontalContainer, 'horizontal', 10);
assert.equal(slots5H.length, 5);
slots5H.forEach((slot, idx) => {
  assert.equal(slot.index, idx);
  assert(slot.bounds.x >= horizontalContainer.x);
  assert(slot.bounds.x + slot.bounds.width <= horizontalContainer.x + horizontalContainer.width + 1);
  assert.equal(slot.bounds.height, 40);
  if (idx > 0) {
    const prev = slots5H[idx - 1];
    assert.equal(slot.bounds.x, prev.bounds.x + prev.bounds.width + 10, 'Horizontal gap must be 10px');
  }
});

// 8 players
const slots8H = computePlayerSlotLayout(8, horizontalContainer, 'horizontal', 8);
assert.equal(slots8H.length, 8);
assert(slots8H[7].bounds.x + slots8H[7].bounds.width <= horizontalContainer.x + horizontalContainer.width + 1);

// 3. Vertical player slots (Dossier matrix)
const verticalContainer = { x: 1200, y: 500, width: 500, height: 300 };

// 5 players vertical
const slots5V = computePlayerSlotLayout(5, verticalContainer, 'vertical', 6);
assert.equal(slots5V.length, 5);
slots5V.forEach((slot, idx) => {
  assert.equal(slot.index, idx);
  assert.equal(slot.bounds.x, verticalContainer.x);
  assert.equal(slot.bounds.width, verticalContainer.width);
  if (idx > 0) {
    const prev = slots5V[idx - 1];
    assert(Math.abs(slot.bounds.y - (prev.bounds.y + prev.bounds.height + 6)) < 1e-4, 'Vertical gap must be 6px');
  }
});

// 4. Edge cases: 1 player and 0 players
const single = computePlayerSlotLayout(1, horizontalContainer, 'horizontal');
assert.equal(single.length, 1);
assert.equal(single[0].bounds.width, horizontalContainer.width);

const zero = computePlayerSlotLayout(0, horizontalContainer, 'horizontal');
assert.equal(zero.length, 1, 'Zero players must safely normalize to at least 1 slot');

console.log('Rhine layout engine: all test suites passed successfully.');
