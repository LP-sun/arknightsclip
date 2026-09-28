import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const out = path.resolve(__dirname, '../../generated/rhine/final_placeholder/frames');
fs.mkdirSync(out, { recursive: true });

const baseUrl = process.env.RHINE_BASE_URL || 'http://127.0.0.1:5173';
const isSmoke = process.env.RHINE_SMOKE === '1' || process.argv.includes('--smoke');

async function loadProjectFrameCount(page) {
  const response = await page.request.get(`${baseUrl}/project.json`);
  if (!response.ok()) {
    throw new Error(`Unable to load project contract (${response.status()} ${response.statusText()})`);
  }

  const project = await response.json();
  const totalFrames = project?.total_frames;
  if (!Number.isInteger(totalFrames) || totalFrames <= 0) {
    throw new Error(`Project contract has invalid total_frames: ${JSON.stringify(totalFrames)}`);
  }
  return totalFrames;
}


const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });

try {
  const totalFrames = await loadProjectFrameCount(page);
  const smokeFrames = [0, 23, 24, 47, 48, totalFrames - 1]
    .filter((frame) => frame >= 0 && frame < totalFrames)
    .filter((frame, index, frames) => frames.indexOf(frame) === index);
  const targetFrames = isSmoke
    ? smokeFrames
    : Array.from({ length: totalFrames }, (_, i) => i);

  console.log(`Starting Rhine render (${targetFrames.length} frames, total_frames: ${totalFrames}, mode: ${isSmoke ? 'SMOKE' : 'FULL'}) against ${baseUrl}`);

  for (const frame of targetFrames) {
    // 1. Explicitly reset READY flag before navigating so state is not inherited
    await page.evaluate(() => {
      window.__RHINE_RENDER_READY__ = false;
      window.__RHINE_RENDER_ERROR__ = null;
    }).catch(() => {});

    // 2. Navigate with domcontentloaded
    const targetUrl = `${baseUrl}/?frame=${frame}`;
    await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 15000 });

    // 3. Wait for explicit window.__RHINE_RENDER_READY__ === true or fail loudly on error
    await page.waitForFunction(
      () => {
        if (window.__RHINE_RENDER_ERROR__) {
          throw new Error(`Rhine render error on frame: ${window.__RHINE_RENDER_ERROR__}`);
        }
        return window.__RHINE_RENDER_READY__ === true;
      },
      null,
      { timeout: 15000 }
    );

    // 4. Save frame capture
    const frameFilename = `${String(frame).padStart(6, '0')}.png`;
    await page.screenshot({ path: path.join(out, frameFilename) });
    console.log(`Rendered frame ${frame} -> ${frameFilename}`);
  }
  console.log(`Successfully completed rendering ${targetFrames.length} frames.`);
} catch (err) {
  console.error('Fatal rendering failure:', err);
  process.exitCode = 1;
} finally {
  await browser.close();
}
