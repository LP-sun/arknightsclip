export interface RhineScene {
  operator_id: string;
  operator_name: string;
  start_frame: number;
  duration_frames: number;
  full_art: string;
  card_art?: string;
  render_mode?: 'hero_art' | 'card_art' | 'metadata_only';
  asset_status?: string;
  profession?: string;
  rarity?: number;
  cards?: { mode: string; path: string };
  players?: any[];
}

export interface RhineProject {
  version: number;
  fps: number;
  width: number;
  height: number;
  player_profiles?: Record<string, any>;
  scenes: RhineScene[];
}

export interface FrameEvaluation {
  frame: number;
  time: number;
  active: number;
  beat: number;
  wave: number;
  camera: {
    x: number;
    y: number;
    roll: number;
  };
}

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

export declare const project: RhineProject;
export declare function evaluate(frame: number): FrameEvaluation;
export declare function getStageZones(): any;
export declare function computePlayerSlotLayout(
  playerCount: number,
  container: Rect,
  orientation?: 'horizontal' | 'vertical',
  gap?: number
): PlayerSlotLayout[];
