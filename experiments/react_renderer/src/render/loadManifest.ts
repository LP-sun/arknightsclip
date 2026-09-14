import fs from 'node:fs';
import path from 'node:path';
import { SceneManifest, LayoutSpec } from '../components/ReportScene.js';

export function loadManifest(manifestPath: string): SceneManifest {
  const absPath = path.resolve(manifestPath);
  if (!fs.existsSync(absPath)) {
    throw new Error(`Manifest file not found: ${absPath}`);
  }
  const content = fs.readFileSync(absPath, 'utf-8');
  return JSON.parse(content) as SceneManifest;
}

export function loadLayout(layoutPath?: string): LayoutSpec {
  const defaultPath = path.resolve(
    __dirname,
    '../../../shared/layout/report_5p_layout.json'
  );
  const targetPath = layoutPath ? path.resolve(layoutPath) : defaultPath;
  if (!fs.existsSync(targetPath)) {
    throw new Error(`Layout specification file not found: ${targetPath}`);
  }
  const content = fs.readFileSync(targetPath, 'utf-8');
  return JSON.parse(content) as LayoutSpec;
}
