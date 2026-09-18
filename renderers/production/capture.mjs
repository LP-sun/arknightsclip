#!/usr/bin/env node
/** Deterministic browser-frame capture and final H.264/AAC assembly. */
import fs from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '../..');
const requireFromRhine = createRequire(path.resolve(ROOT, 'renderers/rhine/package.json'));
const { chromium } = requireFromRhine('playwright');

const args = process.argv.slice(2);
const getArg = (name, fallback) => {
  const index = args.indexOf(name);
  return index >= 0 && args[index + 1] ? args[index + 1] : fallback;
};
const smoke = args.includes('--smoke');
const skipEncode = args.includes('--skip-encode');
const baseUrl = getArg('--base-url', process.env.RHINE_BASE_URL || 'http://127.0.0.1:4173');
const outDir = path.resolve(getArg('--out', path.resolve(ROOT, 'generated/rhine/astra_final')));
const dataFile = path.resolve(getArg('--data', path.resolve(HERE, 'public/project.json')));
const project = JSON.parse(fs.readFileSync(dataFile, 'utf8'));
const allFrames = Array.from({ length: project.totalFrames }, (_, frame) => frame);
const frames = smoke ? [...new Set([0, 1, 23, 24, 49, 50, 51, 120, 600, 1800, project.totalFrames - 2, project.totalFrames - 1])] : allFrames;
const frameDir = path.join(outDir, 'frames');
fs.mkdirSync(frameDir, { recursive: true });

const waitForReady = async (page, frame) => {
  await page.waitForFunction(
    (expectedFrame) => {
      if (window.__RHINE_RENDER_ERROR__) throw new Error(String(window.__RHINE_RENDER_ERROR__));
      return window.__RHINE_RENDER_READY__ === true &&
        (window.__RHINE_RENDER_FRAME__ === undefined || window.__RHINE_RENDER_FRAME__ === expectedFrame);
    },
    frame,
    { timeout: 30000 },
  );
};

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: project.width, height: project.height }, deviceScaleFactor: 1 });
const page = await context.newPage();
page.on('pageerror', (error) => console.error(`[pageerror] ${error.message}`));

try {
  await page.goto(`${baseUrl}/?production=1&frame=0`, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.addStyleTag({ content: '*,*::before,*::after{animation-delay:0s!important;animation-duration:0s!important;transition:none!important}' });
  for (const frame of frames) {
    await page.evaluate(() => {
      window.__RHINE_RENDER_READY__ = false;
      window.__RHINE_RENDER_ERROR__ = null;
    });
    await page.evaluate(async (target) => {
      if (typeof window.renderFrame !== 'function') throw new Error('window.renderFrame(frame) is not defined');
      await window.renderFrame(target);
    }, frame);
    await waitForReady(page, frame);
    await page.screenshot({ path: path.join(frameDir, `${String(frame).padStart(6, '0')}.png`), animations: 'disabled' });
    if (frame % 120 === 0 || smoke) console.log(`[capture] ${frame}/${project.totalFrames - 1}`);
  }
} finally {
  await browser.close();
}

const report = { baseUrl, framesCaptured: frames.length, totalFrames: project.totalFrames, width: project.width, height: project.height, fps: project.fps, smoke, frameDir };
fs.writeFileSync(path.join(outDir, 'capture-report.json'), `${JSON.stringify(report, null, 2)}\n`, 'utf8');

if (!skipEncode && !smoke) {
  const bgm = path.resolve(ROOT, 'bgm及使用指南/明日方舟报菜名（女神异闻录3  月行水上）.mp3');
  const output = path.join(outDir, 'rhine_operator_archive_final.mp4');
  await new Promise((resolve, reject) => {
    const ffmpeg = spawn('ffmpeg', ['-y', '-framerate', String(project.fps), '-i', path.join(frameDir, '%06d.png'), '-i', bgm, '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', String(project.fps), '-c:a', 'aac', '-b:a', '192k', '-t', String(project.durationSeconds), '-movflags', '+faststart', output], { stdio: ['ignore', 'ignore', 'pipe'] });
    ffmpeg.stderr.on('data', (chunk) => process.stderr.write(chunk));
    ffmpeg.on('error', reject);
    ffmpeg.on('close', (code) => code === 0 ? resolve() : reject(new Error(`ffmpeg exited with ${code}`)));
  });
  console.log(`[encode] ${output}`);
}
console.log(JSON.stringify(report));
