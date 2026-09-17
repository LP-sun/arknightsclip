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
const targetFrames = isSmoke
  ? [0, 23, 24, 47, 48, 1007]
  : Array.from({ length: 1008 }, (_, i) => i);

console.log(`Starting Rhine render (${targetFrames.length} frames, mode: ${isSmoke ? 'SMOKE' : 'FULL'}) against ${baseUrl}`);

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });

try {
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
