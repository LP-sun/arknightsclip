import { project, evaluate } from './timeline.js';

const canvas = document.querySelector('canvas') as HTMLCanvasElement;
const ctx = canvas.getContext('2d')!;
const frame = Number(new URLSearchParams(location.search).get('frame') ?? 0);

// Reset render lifecycle flags at initialization
(window as any).__RHINE_RENDER_READY__ = false;
(window as any).__RHINE_RENDER_ERROR__ = null;

const draw = () => {
  try {
    const s = evaluate(frame);
    const op = project.scenes[s.active];
    if (!op) {
      throw new RangeError(`Scene not found for frame ${frame} (active scene index: ${s.active})`);
    }

    ctx.fillStyle = '#dfe7e8';
    ctx.fillRect(0, 0, 1920, 1080);
    ctx.strokeStyle = '#92a4a6';

    for (let y = 90; y < 1000; y += 150) {
      for (let x = 80; x < 2000; x += 170) {
        const w = Math.exp(-((x / 170 - (s.active * 1.8 + frame * 0.035)) ** 2) / 0.7);
        ctx.globalAlpha = 0.18 + 0.36 * w;
        ctx.strokeRect(x + (y % 300) / 6, y + w * 35, 120, 90);
      }
    }

    ctx.globalAlpha = 1;
    ctx.fillStyle = '#26383d';
    ctx.font = '28px monospace';
    ctx.fillText('RHINE LAB // ARCHIVE ACCESS', 80, 70);

    ctx.font = '22px monospace';
    const totalFrames = project.scenes.length * project.fps;
    ctx.fillText(
      `SCANNING ${String(frame).padStart(4, '0')} / ${String(totalFrames).padStart(4, '0')}`,
      80,
      1020
    );
    ctx.fillText('DATA ACCESS  •  ARCHIVE PENDING', 1450, 70);

    const cx = 960 + s.camera.x;
    ctx.strokeStyle = '#fff';
    ctx.strokeRect(cx - 280, 140, 560, 820);
    ctx.fillStyle = '#fff';
    ctx.font = '64px sans-serif';
    ctx.fillText(op.operator_name, cx - 250, 930);
    ctx.font = '28px monospace';
    ctx.fillText(op.full_art ? 'RESOLVED' : 'DATA PENDING', cx - 170, 550);

    // Frame rendered successfully
    (window as any).__RHINE_RENDER_READY__ = true;
  } catch (err: any) {
    (window as any).__RHINE_RENDER_READY__ = false;
    (window as any).__RHINE_RENDER_ERROR__ = err?.message || String(err);
    console.error('Fatal Rhine render error during draw:', err);
    throw err;
  }
};

// Fail loudly on project contract load failure - NO silent fallback!
fetch('/project.json')
  .then((response) => {
    if (!response.ok) {
      throw new Error(`Failed to load /project.json: HTTP ${response.status} ${response.statusText}`);
    }
    return response.json();
  })
  .then((data) => {
    if (!data || !Array.isArray(data.scenes) || data.scenes.length === 0) {
      throw new Error('Invalid project.json contract: scenes array is missing or empty');
    }
    project.scenes.splice(0, project.scenes.length, ...data.scenes);
    if (typeof data.fps === 'number') project.fps = data.fps;
    if (typeof data.width === 'number') project.width = data.width;
    if (typeof data.height === 'number') project.height = data.height;
    draw();
  })
  .catch((err: any) => {
    (window as any).__RHINE_RENDER_READY__ = false;
    (window as any).__RHINE_RENDER_ERROR__ = err?.message || String(err);
    console.error('Fatal Rhine contract load failure:', err);

    // Display visible error banner on canvas for diagnostics
    ctx.fillStyle = '#4a0e0e';
    ctx.fillRect(0, 0, 1920, 1080);
    ctx.fillStyle = '#ff6b6b';
    ctx.font = '36px monospace';
    ctx.fillText('FATAL: RHINE PROJECT CONTRACT LOAD FAILED', 80, 120);
    ctx.fillStyle = '#ffffff';
    ctx.font = '24px monospace';
    ctx.fillText(err?.message || String(err), 80, 180);
    ctx.fillText('Ensure /project.json is generated into renderers/rhine/public/project.json', 80, 230);
  });
