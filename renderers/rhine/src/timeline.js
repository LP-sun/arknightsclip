export const project = {
  version: 1,
  fps: 24,
  width: 1920,
  height: 1080,
  scenes: Array.from({ length: 42 }, (_, i) => ({
    operator_id: `manifest_${i + 1}`,
    operator_name: `ARCHIVE ${String(i + 1).padStart(2, '0')}`,
    start_frame: i * 24,
    duration_frames: 24,
    full_art: '',
    cards: { mode: 'full_layer', path: '' }
  }))
};

/**
 * Derives presentation state deterministically from integer frame index.
 * @param {number} frame
 */
export function evaluate(frame) {
  if (!Number.isInteger(frame) || frame < 0 || frame >= project.scenes.length * 24) {
    throw new RangeError(`frame out of range: ${frame}`);
  }
  const active = Math.floor(frame / 24);
  const beat = (frame % 24) / 24;
  return {
    frame,
    time: frame / project.fps,
    active,
    beat,
    wave: Math.exp(-((beat - 0.38) ** 2) / 0.08),
    camera: {
      x: Math.sin((frame / 24) * 0.45) * 120,
      y: Math.cos((frame / 24) * 0.35) * 14,
      roll: Math.sin((frame / 24) * 0.2) * 0.012
    }
  };
}
