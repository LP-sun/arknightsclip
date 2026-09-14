import path from 'node:path';
import { renderScene } from '../src/render/renderScene.js';

function parseArgs() {
  const args = process.argv.slice(2);
  let manifest = '';
  let output = '';
  let layout = '';

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--manifest' && args[i + 1]) {
      manifest = args[i + 1];
      i++;
    } else if (args[i] === '--output' && args[i + 1]) {
      output = args[i + 1];
      i++;
    } else if (args[i] === '--layout' && args[i + 1]) {
      layout = args[i + 1];
      i++;
    }
  }

  if (!manifest || !output) {
    console.error('Usage: npm run render -- --manifest <manifest.json> --output <output.png> [--layout <layout.json>]');
    process.exit(1);
  }

  return { manifest, output, layout };
}

async function main() {
  const { manifest, output, layout } = parseArgs();
  console.log(`[ReactRenderer] Rendering scene from: ${manifest}`);
  console.log(`[ReactRenderer] Output target: ${output}`);

  try {
    const meta = await renderScene({
      manifestPath: manifest,
      outputPath: output,
      layoutPath: layout || undefined,
    });
    console.log(JSON.stringify(meta, null, 2));
  } catch (err) {
    console.error('[ReactRenderer] Render failed:', err);
    process.exit(1);
  }
}

main();
