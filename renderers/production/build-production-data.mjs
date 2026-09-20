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
  const destination = path.resolve(OUT_DIR, relative);
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.copyFileSync(absolute, destination);
  return `/${relative}`;
};
const repairedCard = (value) => {
  if (!value) return value;
  const ext = path.extname(value);
  const candidate = `${value.slice(0, -ext.length)}_enhanced${ext}`;
  return fs.existsSync(candidate) ? candidate : value;
};

const readJson = (file) => JSON.parse(fs.readFileSync(file, 'utf8'));
const profileNames = Object.fromEntries(['P1','P2','P3','P4','P5'].flatMap(id => {
  const file = path.resolve(ROOT, 'data/raw', id, 'profile.json');
  if (!fs.existsSync(file)) return [];
  const p = readJson(file); return [[id, p.display_name || id]];
}));
const source = readJson(INPUT);
const registry = readJson(path.resolve(ROOT, 'src/arknightsclip/registry/operator_registry.json'));
const professionById = Object.fromEntries((registry.operators ?? registry ?? []).map((x) => [x.char_id || x.operator_id, x.profession || 'UNKNOWN']));
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
      owned: typeof state.own === 'boolean' ? state.own : null,
      elite: state.elite ?? null,
      level: state.level ?? null,
      potential: state.potential ?? null,
      rarity: Number(state.rarity ?? 6),
      card: rootRelativeUrl(repairedCard(item.cards?.[id])),
      // Only the portrait region may be reused: donor cards contain another
      // player's embedded levels and must never be displayed as this record.
      // Never borrow another player's card or portrait. A missing source card
      // must remain visibly missing until that player's emulator is captured.
      portraitFallback: null,
      art: null,
      needsReview: Boolean(state.needs_review),
    };
  });
  operators.push({
    index: Number(item.index),
    name: item.name || item.canonical_name || operatorId,
    canonicalName: item.canonical_name || item.name || operatorId,
    operatorId,
    profession: professionById[operatorId] || 'UNKNOWN',
    source: 'Local operator registry',
    startFrame: cursor,
    endFrame: cursor + durationFrames,
    durationFrames,
    art: fs.existsSync(artCandidate) ? rootRelativeUrl(artCandidate) : null,
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
  identities: ['P1','P2','P3','P4','P5'].map(id => ({id, displayName: profileNames[id] || id, image: rootRelativeUrl([path.join(ROOT,'data/player_cards',`${id}-crop.png`)].find(p=>fs.existsSync(p)))})),
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
