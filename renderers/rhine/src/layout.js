/**
 * Rhine Stage Layout Engine.
 *
 * Decouples Rhine renderer from legacy Pen 5-slot/8-slot hardcoded geometry.
 * All layouts are computed parametrically within the 1920x1080 design stage.
 */

export const STAGE_CONFIG = {
  width: 1920,
  height: 1080,
  margins: {
    top: 36,
    right: 40,
    bottom: 36,
    left: 40,
  },
  headerHeight: 74,
  footerHeight: 44,
};

/**
 * Computes standard architectural stage zones for the 1920x1080 canvas.
 */
export function getStageZones() {
  const { width, height, margins, headerHeight, footerHeight } = STAGE_CONFIG;
  const safeW = width - margins.left - margins.right;
  const safeH = height - margins.top - margins.bottom;

  const safeArea = {
    x: margins.left,
    y: margins.top,
    width: safeW,
    height: safeH,
  };

  const header = {
    x: safeArea.x + 32,
    y: safeArea.y + 4,
    width: safeW - 64,
    height: headerHeight,
  };

  const footer = {
    x: safeArea.x + 32,
    y: safeArea.y + safeH - footerHeight,
    width: safeW - 64,
    height: footerHeight,
  };

  const content = {
    x: safeArea.x + 20,
    y: header.y + header.height + 10,
    width: safeW - 40,
    height: footer.y - (header.y + header.height + 20),
  };

  return {
    canvas: { x: 0, y: 0, width, height },
    safeArea,
    header,
    footer,
    content,
  };
}

/**
 * Computes responsive slot rectangles for N players.
 * Supports arbitrary player counts (1 to 8+) rather than being hardcoded to 5 or 8 slots.
 */
export function computePlayerSlotLayout(
  playerCount,
  container,
  orientation = 'horizontal',
  gap = 10
) {
  const count = Math.max(1, playerCount);
  const slots = [];

  if (orientation === 'horizontal') {
    const totalGaps = (count - 1) * gap;
    const availableWidth = container.width - totalGaps;
    const slotW = Math.max(80, availableWidth / count);
    const slotH = container.height;

    for (let i = 0; i < count; i++) {
      slots.push({
        index: i,
        bounds: {
          x: container.x + i * (slotW + gap),
          y: container.y,
          width: slotW,
          height: slotH,
        },
      });
    }
  } else {
    // Vertical layout
    const totalGaps = (count - 1) * gap;
    const availableHeight = container.height - totalGaps;
    const slotH = Math.max(26, availableHeight / count);
    const slotW = container.width;

    for (let i = 0; i < count; i++) {
      slots.push({
        index: i,
        bounds: {
          x: container.x,
          y: container.y + i * (slotH + gap),
          width: slotW,
          height: slotH,
        },
      });
    }
  }

  return slots;
}
