export interface RhineScene {
  operator_id: string;
  operator_name: string;
  start_frame: number;
  duration_frames: number;
  full_art: string;
  cards?: { mode: string; path: string };
  players?: any[];
}

export interface RhineProject {
  version: number;
  fps: number;
  width: number;
  height: number;
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

export declare const project: RhineProject;
export declare function evaluate(frame: number): FrameEvaluation;
