import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';
import { renderScene, RenderMetadata } from '../src/render/renderScene.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function batchRender() {
  const sharedManifestsDir = path.resolve(__dirname, '../../shared/manifests');
  const outputDir = path.resolve(__dirname, '../outputs');

  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const files = fs.readdirSync(sharedManifestsDir).filter(f => f.endsWith('.json'));
  console.log(`[ReactRenderer] Found ${files.length} manifests to render in: ${sharedManifestsDir}`);

  // 复用同一个 Chromium 浏览器实例加速批处理
  let browser;
  try {
    browser = await chromium.launch({ channel: 'msedge', headless: true });
  } catch {
    browser = await chromium.launch({ headless: true });
  }
  const results: RenderMetadata[] = [];
  const t0 = performance.now();

  try {
    for (const file of files) {
      const manifestPath = path.join(sharedManifestsDir, file);
      const outputName = file.replace('.json', '.png');
      const outputPath = path.join(outputDir, outputName);

      console.log(`  -> Rendering ${file} to ${outputName}...`);
      const meta = await renderScene({
        manifestPath,
        outputPath,
        browserInstance: browser,
      });
      results.push(meta);
    }
  } finally {
    await browser.close();
  }

  const totalTime = ((performance.now() - t0) / 1000).toFixed(4);
  console.log(`[ReactRenderer] Batch completed ${results.length} scenes in ${totalTime}s!`);
  console.log(JSON.stringify(results, null, 2));
}

batchRender().catch(err => {
  console.error('[ReactRenderer] Batch failed:', err);
  process.exit(1);
});
