#!/usr/bin/env node
/**
 * Adapt the five-player comparison manifest into the stable contract consumed
 * by the production DOM/Three renderer.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '../..');
const INPUT = path.resolve(ROOT, 'generated/rhine/five_player_comparison_v1/comparison_manifest.json');
const OUT_DIR = path.resolve(HERE, 'public');
const OUTPUT = path.resolve(OUT_DIR, 'project.json');

const toPosix = (value) => value.split(path.sep).join('/');
const rootRelativeUrl = (value) => {
  if (!value) return null;
  const absolute = path.isAbsolute(value) ? path.normalize(value) : path.resolve(ROOT, value);
  if (!fs.existsSync(absolute)) return null;
  const relative = toPosix(path.relative(ROOT, absolute));
  return `/${relative}`;
};

const readJson = (file) => JSON.parse(fs.readFileSync(file, 'utf8'));
const source = readJson(INPUT);
const operators = [];
let cursor = Number(source.intro_frames ?? 50);

for (const item of source.operators ?? []) {
  const durationFrames = Math.max(1, Number(item.duration_frames ?? 1));
  const operatorId = item.operator_id || `unknown_${item.index}`;
  const artCandidate = path.resolve(ROOT, 'assets/operators', operatorId, 'full.png');
  const players = ['P1', 'P2', 'P3', 'P4', 'P5'].map((id) => {
    const state = item.states?.[id] ?? {};
    return {
      id,
      owned: Boolean(state.own),
      elite: Number(state.elite ?? 0),
      level: Number(state.level ?? 1),
      potential: Number(state.potential ?? 1),
      rarity: Number(state.rarity ?? 6),
      card: rootRelativeUrl(item.cards?.[id]),
      needsReview: Boolean(state.needs_review),
    };
  });
  operators.push({
    index: Number(item.index),
    name: item.name || item.canonical_name || operatorId,
    canonicalName: item.canonical_name || item.name || operatorId,
    operatorId,
    startFrame: cursor,
    endFrame: cursor + durationFrames,
    durationFrames,
    art: fs.existsSync(artCandidate) ? `/assets/operators/${operatorId}/full.png` : null,
    players,
  });
  cursor += durationFrames;
}

const project = {
  version: 2,
  kind: 'rhine_operator_archive_production',
  fps: Number(source.fps ?? 24),
  width: Number(source.width ?? 1920),
  height: Number(source.height ?? 1080),
  introFrames: Number(source.intro_frames ?? 50),
  totalFrames: Number(source.total_frames ?? cursor),
  durationSeconds: Number(source.total_frames ?? cursor) / Number(source.fps ?? 24),
  audio: {
    src: '/bgm及使用指南/明日方舟报菜名（女神异闻录3  月行水上）.mp3',
    trimSeconds: Number(source.total_frames ?? cursor) / Number(source.fps ?? 24),
  },
  sourceManifest: '/generated/rhine/five_player_comparison_v1/comparison_manifest.json',
  operators,
};

if (project.totalFrames !== cursor) {
  // Preserve the source timeline as the authority, while retaining a useful
  // diagnostic for renderers that validate the final segment boundaries.
  project.timelineFrames = cursor;
}

fs.mkdirSync(OUT_DIR, { recursive: true });
fs.writeFileSync(OUTPUT, `${JSON.stringify(project, null, 2)}\n`, 'utf8');
console.log(JSON.stringify({ output: OUTPUT, operators: operators.length, frames: project.totalFrames, fps: project.fps }));
