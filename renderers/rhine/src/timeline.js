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

  // Continuous multi-frequency camera motion: macro flow + micro rhythm
  const macroX = Math.sin((frame / 24) * 0.45) * 90;
  const macroY = Math.cos((frame / 24) * 0.35) * 12;
  const microX = Math.sin(beat * Math.PI) * 5;
  const microY = Math.cos(beat * Math.PI) * 3;

  // Smooth 0.20s transition momentum (enter sweep / steady breath / exit handoff)
  let transitionPhase = 'steady';
  let transitionProgress = 0;
  let panelShiftX = 0;
  let panelAlpha = 1.0;

  if (beat < 0.20) {
    // 0.20s entrance: smooth deceleration into focus
    transitionPhase = 'enter';
    transitionProgress = beat / 0.20;
    const ease = 1 - Math.pow(1 - transitionProgress, 3);
    panelShiftX = (1 - ease) * 38;
    panelAlpha = 0.6 + 0.4 * ease;
  } else if (beat > 0.82) {
    // 0.18s exit: subtle forward velocity handoff to next operator
    transitionPhase = 'exit';
    transitionProgress = (beat - 0.82) / 0.18;
    const ease = Math.pow(transitionProgress, 2);
    panelShiftX = -ease * 20;
    panelAlpha = 1.0 - 0.2 * ease;
  }

  return {
    frame,
    time: frame / project.fps,
    active,
    beat,
    wave: Math.exp(-((beat - 0.38) ** 2) / 0.08),
    camera: {
      x: macroX + microX,
      y: macroY + microY,
      roll: Math.sin((frame / 24) * 0.2) * 0.008
    },
    motion: {
      phase: transitionPhase,
      progress: transitionProgress,
      shiftX: panelShiftX,
      alpha: panelAlpha,
      zoom: 1.0 + Math.sin(beat * Math.PI) * 0.01
    }
  };
}
