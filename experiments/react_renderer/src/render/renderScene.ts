import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import React from 'react';
import { renderToString } from 'react-dom/server';
import { chromium, Browser } from 'playwright';
import { ReportScene, SceneManifest, LayoutSpec } from '../components/ReportScene.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export interface RenderOptions {
  manifestPath: string;
  outputPath: string;
  layoutPath?: string;
  sharedDir?: string;
  browserInstance?: Browser;
}

export interface RenderMetadata {
  manifest: string;
  operator_id: string;
  operator_name: string;
  resolution: [number, number];
  render_time_seconds: number;
  output_png: string;
  status: string;
}

export async function renderScene(options: RenderOptions): Promise<RenderMetadata> {
  const t0 = performance.now();

  const absManifestPath = path.resolve(options.manifestPath);
  const absOutputPath = path.resolve(options.outputPath);
  osEnsureDir(path.dirname(absOutputPath));

  // 1. 读取 Manifest 与 Layout
  const manifestContent = fs.readFileSync(absManifestPath, 'utf-8');
  const manifest = JSON.parse(manifestContent) as SceneManifest;

  const sharedDir = options.sharedDir
    ? path.resolve(options.sharedDir)
    : path.resolve(__dirname, '../../../shared');

  const defaultLayoutPath = path.join(sharedDir, 'layout', 'report_5p_layout.json');
  const absLayoutPath = options.layoutPath ? path.resolve(options.layoutPath) : defaultLayoutPath;
  const layoutContent = fs.readFileSync(absLayoutPath, 'utf-8');
  const layout = JSON.parse(layoutContent) as LayoutSpec;

  // 2. 格式化资源 URL 为本地 file:/// 路径以支持 Playwright 读取
  const assetBaseUrl = 'file:///' + sharedDir.replace(/\\/g, '/') + '/';

  // 3. 读取 CSS 样式
  const cssPath = path.resolve(__dirname, '../styles/report.css');
  const cssContent = fs.readFileSync(cssPath, 'utf-8');

  // 4. React 服务端渲染 (SSR to string)
  const sceneElement = React.createElement(ReportScene, {
    manifest,
    layout,
    assetBaseUrl,
  });
  const sceneHtml = renderToString(sceneElement);

  // 5. 组合完整 HTML 文档
  const fullHtml = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=1920, height=1080, initial-scale=1.0">
  <title>ARKNIGHTS OPERATOR REPORT</title>
  <style>
${cssContent}
  </style>
</head>
<body>
  ${sceneHtml}
</body>
</html>`;

  // 6. 启动/复用 Chromium 实例
  const ownsBrowser = !options.browserInstance;
  let browser = options.browserInstance;
  if (!browser) {
    try {
      browser = await chromium.launch({ channel: 'msedge', headless: true });
    } catch {
      browser = await chromium.launch({ headless: true });
    }
  }

  try {
    const page = await browser.newPage({
      viewport: { width: 1920, height: 1080 },
      deviceScaleFactor: 1,
    });

    // 加载 HTML
    await page.setContent(fullHtml, { waitUntil: 'load' });

    // 等待中文字体加载完毕
    await page.evaluate(async () => {
      await document.fonts.ready;
    });

    // 等待所有 <img> 元素加载完毕
    await page.evaluate(async () => {
      const images = Array.from(document.images);
      await Promise.all(
        images.map((img) => {
          if (img.complete) return Promise.resolve();
          return new Promise((resolve) => {
            img.onload = img.onerror = resolve;
          });
        })
      );
    });

    // 截图保存 1920x1080 PNG
    await page.screenshot({
      path: absOutputPath,
      type: 'png',
      omitBackground: false,
    });

    await page.close();
  } finally {
    if (ownsBrowser) {
      await browser.close();
    }
  }

  const durationSec = (performance.now() - t0) / 1000;
  return {
    manifest: absManifestPath,
    operator_id: manifest.operator.id,
    operator_name: manifest.operator.name,
    resolution: [1920, 1080],
    render_time_seconds: Number(durationSec.toFixed(4)),
    output_png: absOutputPath,
    status: 'SUCCESS',
  };
}

function osEnsureDir(dirPath: string) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}
