export interface Rect {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface PlayerSlotLayout {
  index: number;
  bounds: Rect;
}

export interface StageZones {
  canvas: Rect;
  safeArea: Rect;
  header: Rect;
  footer: Rect;
  content: Rect;
}

export declare const STAGE_CONFIG: {
  width: number;
  height: number;
  margins: {
    top: number;
    right: number;
    bottom: number;
    left: number;
  };
  headerHeight: number;
  footerHeight: number;
};

export declare function getStageZones(): StageZones;

export declare function computePlayerSlotLayout(
  playerCount: number,
  container: Rect,
  orientation?: 'horizontal' | 'vertical',
  gap?: number
): PlayerSlotLayout[];
