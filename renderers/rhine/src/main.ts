import { project, evaluate } from './timeline.js';
import { getStageZones, computePlayerSlotLayout } from './layout.js';

const canvas = document.querySelector('canvas') as HTMLCanvasElement;
const ctx = canvas.getContext('2d')!;
const frame = Number(new URLSearchParams(location.search).get('frame') ?? 0);

// Reset render lifecycle flags at initialization
(window as any).__RHINE_RENDER_READY__ = false;
(window as any).__RHINE_RENDER_ERROR__ = null;

// Helper to draw corner reticles for technical styling
function drawCornerReticles(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  size = 14,
  color = '#4fd1c5'
) {
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;

  // Top-left
  ctx.beginPath();
  ctx.moveTo(x, y + size);
  ctx.lineTo(x, y);
  ctx.lineTo(x + size, y);
  ctx.stroke();

  // Top-right
  ctx.beginPath();
  ctx.moveTo(x + w - size, y);
  ctx.lineTo(x + w, y);
  ctx.lineTo(x + w, y + size);
  ctx.stroke();

  // Bottom-left
  ctx.beginPath();
  ctx.moveTo(x, y + h - size);
  ctx.lineTo(x, y + h);
  ctx.lineTo(x + size, y + h);
  ctx.stroke();

  // Bottom-right
  ctx.beginPath();
  ctx.moveTo(x + w - size, y + h);
  ctx.lineTo(x + w, y + h);
  ctx.lineTo(x + w, y + h - size);
  ctx.stroke();
}

const draw = () => {
  try {
    const s = evaluate(frame);
    const op = project.scenes[s.active];
    if (!op) {
      throw new RangeError(`Scene not found for frame ${frame} (active scene index: ${s.active})`);
    }

    // Determine formal render mode
    const mode = op.render_mode || (op.full_art ? 'hero_art' : op.card_art ? 'card_art' : 'metadata_only');

    // 1. Dark Lab Background with depth grid
    ctx.fillStyle = '#06131a';
    ctx.fillRect(0, 0, 1920, 1080);

    // Dynamic continuous grid lines with flowing parallax across transitions
    ctx.strokeStyle = '#0f2c38';
    ctx.lineWidth = 1;
    const gridShiftX = (frame * 1.2) % 160;
    for (let y = 100; y < 1000; y += 120) {
      ctx.beginPath();
      ctx.moveTo(60, y);
      ctx.lineTo(1860, y);
      ctx.stroke();
    }
    for (let x = -60; x < 2000; x += 160) {
      const gx = x + gridShiftX;
      if (gx >= 60 && gx <= 1860) {
        ctx.beginPath();
        ctx.moveTo(gx, 100);
        ctx.lineTo(gx, 1000);
        ctx.stroke();
      }
    }

    // Ambient continuous scan wave animation across timeline
    for (let y = 90; y < 1000; y += 150) {
      for (let x = 80; x < 2000; x += 170) {
        const continuousPhase = (frame * 0.045) % 12;
        const w = Math.exp(-((x / 170 - continuousPhase) ** 2) / 0.85);
        ctx.strokeStyle = '#1d5a6a';
        ctx.globalAlpha = 0.12 + 0.28 * w;
        ctx.strokeRect(x + (y % 300) / 6, y + w * 28, 120, 90);
      }
    }
    ctx.globalAlpha = 1.0;

    const zones = getStageZones();

    // Outer architectural safety border
    ctx.strokeStyle = '#225566';
    ctx.lineWidth = 2;
    ctx.strokeRect(zones.safeArea.x, zones.safeArea.y, zones.safeArea.width, zones.safeArea.height);
    drawCornerReticles(ctx, zones.safeArea.x, zones.safeArea.y, zones.safeArea.width, zones.safeArea.height, 20, '#38b2ac');

    // 2. Top Header Telemetry
    ctx.fillStyle = '#64d2c8';
    ctx.font = 'bold 26px monospace';
    ctx.fillText('RHINE LAB // ARCHIVE SPECIMEN ACCESS', zones.header.x, zones.header.y + 36);

    ctx.fillStyle = '#2c7a88';
    ctx.font = '18px monospace';
    ctx.fillText('RHI-07 // SECURE RETRIEVAL PROTOCOL  •  SPECIMEN ARCHIVE SYSTEM', zones.header.x + 2, zones.header.y + 64);

    ctx.fillStyle = '#4fd1c5';
    ctx.font = '18px monospace';
    ctx.fillText('SYSTEM STATUS: NOMINAL  •  SECURITY CLEARANCE LV.3', zones.header.x + zones.header.width - 520, zones.header.y + 36);

    // Continuous timeline progress ribbon across sequence
    const totalFrames = project.scenes.length * project.fps;
    const timelineProgress = Math.min(1.0, frame / Math.max(1, totalFrames));
    const ribbonW = 320;
    const ribbonH = 6;
    const ribbonX = zones.header.x + zones.header.width - ribbonW;
    const ribbonY = zones.header.y + 48;
    ctx.fillStyle = '#142834';
    ctx.fillRect(ribbonX, ribbonY, ribbonW, ribbonH);
    ctx.fillStyle = '#4fd1c5';
    ctx.fillRect(ribbonX, ribbonY, ribbonW * timelineProgress, ribbonH);
    ctx.fillStyle = '#81e6d9';
    ctx.fillRect(ribbonX + ribbonW * timelineProgress - 2, ribbonY - 2, 4, ribbonH + 4);

    // 3. Bottom Footer Telemetry
    ctx.fillStyle = '#718096';
    ctx.font = '18px monospace';
    ctx.fillText(
      `FRAME [${String(frame).padStart(4, '0')} / ${String(totalFrames).padStart(4, '0')}]   BEAT [${s.beat.toFixed(2)}]   CAMERA [X:${s.camera.x.toFixed(1)} Y:${s.camera.y.toFixed(1)}]`,
      zones.footer.x,
      zones.footer.y + 28
    );
    ctx.fillText('1920x1080  •  24.0 FPS  •  CONTINUOUS FLOW ENGINE', zones.footer.x + zones.footer.width - 440, zones.footer.y + 28);

    // Central camera-responsive positioning with smooth transition momentum
    const shiftX = s.motion?.shiftX ?? 0;
    const panelAlpha = s.motion?.alpha ?? 1.0;
    const cx = 960 + s.camera.x + shiftX;
    const cy = 540 + s.camera.y;

    // Apply smooth opacity momentum
    ctx.globalAlpha = panelAlpha;

    // 4. Render Modes: hero-art mode vs first-class card-art fallback mode
    if (mode === 'hero_art') {
      // --- MODE A: HERO ARTWORK PRESENTATION ---
      const pw = 840;
      const ph = 740;
      const px = cx - pw / 2;
      const py = cy - ph / 2 + 10;

      // Specimen main panel background
      ctx.fillStyle = 'rgba(10, 28, 38, 0.88)';
      ctx.fillRect(px, py, pw, ph);

      // Specimen panel border & corners
      ctx.strokeStyle = '#2c7a88';
      ctx.lineWidth = 2;
      ctx.strokeRect(px, py, pw, ph);
      drawCornerReticles(ctx, px, py, pw, ph, 16, '#64d2c8');

      // Top title bar inside specimen frame
      ctx.fillStyle = '#143c4a';
      ctx.fillRect(px + 4, py + 4, pw - 8, 38);
      ctx.fillStyle = '#81e6d9';
      ctx.font = 'bold 16px monospace';
      ctx.fillText(`SPECIMEN // ${op.operator_id.toUpperCase()}  [HERO ART RESOLVED]`, px + 20, py + 28);
      ctx.fillText(`ARCHIVE NO.${String(s.active + 1).padStart(3, '0')}`, px + pw - 180, py + 28);

      // Procedural scanner sweep
      const scanY = py + 42 + ((frame * 12) % (ph - 180));
      ctx.fillStyle = 'rgba(79, 209, 197, 0.15)';
      ctx.fillRect(px + 4, scanY, pw - 8, 4);

      // Center visual placeholder framing
      ctx.strokeStyle = 'rgba(79, 209, 197, 0.3)';
      ctx.strokeRect(px + 40, py + 60, pw - 80, ph - 220);

      // Center title and identity
      ctx.fillStyle = '#e6fffa';
      ctx.font = 'bold 54px sans-serif';
      ctx.fillText(op.operator_name, px + 50, py + ph - 110);

      ctx.fillStyle = '#4fd1c5';
      ctx.font = '22px monospace';
      const rarityStr = '★'.repeat(op.rarity || 6);
      ctx.fillText(`${rarityStr}   CLASS // ${op.profession || 'OPERATOR'}   HERO ARTWORK ACTIVE`, px + 54, py + ph - 68);

      // Player ownership indicators - parameterized responsive slot layout
      const players = op.players || [];
      const badgeContainer = {
        x: px + 40,
        y: py + ph - 44,
        width: pw - 80,
        height: 32,
      };
      const slotLayouts = computePlayerSlotLayout(players.length, badgeContainer, 'horizontal', 10);

      players.forEach((p: any, idx: number) => {
        const slot = slotLayouts[idx];
        if (!slot) return;
        const { x: bx, y: by, width: bw, height: bh } = slot.bounds;
        const owned = p.status === 'confirmed_owned' || p.own === true;
        ctx.fillStyle = owned ? '#1a4149' : '#141c22';
        ctx.fillRect(bx, by, bw, bh);
        ctx.strokeStyle = owned ? '#38b2ac' : '#32404e';
        ctx.lineWidth = 1.5;
        ctx.strokeRect(bx, by, bw, bh);

        ctx.fillStyle = owned ? '#4fd1c5' : '#718096';
        ctx.font = 'bold 12px monospace';
        const pid = p.player_id || `P${idx + 1}`;
        const dName = p.display_name ? p.display_name.slice(0, 4) : pid;
        ctx.fillText(`${pid} ${dName}`, bx + 8, by + 14);

        ctx.fillStyle = owned ? '#b2f5ea' : '#4a5568';
        ctx.font = '11px monospace';
        const st = owned ? `E${p.elite ?? 2} L${p.level ?? 60} P${p.potential ?? 1}` : 'NO INFO';
        ctx.fillText(st, bx + 8, by + 26);
      });

    } else if (mode === 'card_art') {
      // --- MODE B: FIRST-CLASS CARD-ART SPECIMEN FALLBACK ---
      const cw = 500;
      const ch = 740;
      const cx0 = cx - 360;
      const cy0 = cy - ch / 2 + 10;

      // Card specimen frame (Left side)
      ctx.fillStyle = 'rgba(9, 25, 34, 0.92)';
      ctx.fillRect(cx0, cy0, cw, ch);
      ctx.strokeStyle = '#285e61';
      ctx.lineWidth = 2;
      ctx.strokeRect(cx0, cy0, cw, ch);
      drawCornerReticles(ctx, cx0, cy0, cw, ch, 16, '#4fd1c5');

      // Card header tag
      ctx.fillStyle = '#1a3644';
      ctx.fillRect(cx0 + 4, cy0 + 4, cw - 8, 38);
      ctx.fillStyle = '#4fd1c5';
      ctx.font = 'bold 16px monospace';
      ctx.fillText('ARCHIVE SPECIMEN // OPERBOX CARD', cx0 + 20, cy0 + 28);
      ctx.fillText(`NO.${String(s.active + 1).padStart(3, '0')}`, cx0 + cw - 90, cy0 + 28);

      // Card visual presentation container
      const cardInnerX = cx0 + 50;
      const cardInnerY = cy0 + 60;
      const cardInnerW = cw - 100;
      const cardInnerH = ch - 180;
      ctx.fillStyle = '#06161f';
      ctx.fillRect(cardInnerX, cardInnerY, cardInnerW, cardInnerH);
      ctx.strokeStyle = '#319795';
      ctx.strokeRect(cardInnerX, cardInnerY, cardInnerW, cardInnerH);

      // Card interior graphic lines (procedural specimen reticle)
      ctx.strokeStyle = 'rgba(79, 209, 197, 0.25)';
      ctx.beginPath();
      ctx.moveTo(cardInnerX, cardInnerY);
      ctx.lineTo(cardInnerX + cardInnerW, cardInnerY + cardInnerH);
      ctx.moveTo(cardInnerX + cardInnerW, cardInnerY);
      ctx.lineTo(cardInnerX, cardInnerY + cardInnerH);
      ctx.stroke();

      ctx.fillStyle = '#b2f5ea';
      ctx.font = 'bold 20px monospace';
      ctx.fillText('OPERBOX CARD SPECIMEN', cardInnerX + 60, cardInnerY + cardInnerH / 2 - 10);
      ctx.fillStyle = '#4fd1c5';
      ctx.font = '15px monospace';
      ctx.fillText(op.card_art || 'CARDS_RAW ARCHIVE DATA', cardInnerX + 40, cardInnerY + cardInnerH / 2 + 20);

      // Card bottom name
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 36px sans-serif';
      ctx.fillText(op.operator_name, cx0 + 50, cy0 + ch - 65);
      ctx.fillStyle = '#38b2ac';
      ctx.font = '16px monospace';
      ctx.fillText(`CLASS // ${op.profession || 'OPERATOR'}   ID: ${op.operator_id}`, cx0 + 52, cy0 + ch - 35);

      // Right Telemetry Dossier Panel
      const dw = 580;
      const dh = ch;
      const dx0 = cx + 180;
      const dy0 = cy0;

      ctx.fillStyle = 'rgba(8, 22, 30, 0.88)';
      ctx.fillRect(dx0, dy0, dw, dh);
      ctx.strokeStyle = '#234e52';
      ctx.strokeRect(dx0, dy0, dw, dh);
      drawCornerReticles(ctx, dx0, dy0, dw, dh, 14, '#38b2ac');

      ctx.fillStyle = '#16333e';
      ctx.fillRect(dx0 + 4, dy0 + 4, dw - 8, 38);
      ctx.fillStyle = '#81e6d9';
      ctx.font = 'bold 16px monospace';
      ctx.fillText('RHINE ARCHIVE SPECIFICATION // SPECIMEN DOSSIER', dx0 + 20, dy0 + 28);

      // Telemetry fields
      const rows = [
        ['SUBJECT IDENTIFIER', op.operator_name],
        ['CANONICAL ID', op.operator_id],
        ['ARCHIVE TIER', '6-STAR RARITY SPECIMEN'],
        ['SPECIMEN MODE', 'FIRST-CLASS CARD-ART FALLBACK'],
        ['CAPTURE SOURCE', 'OPERBOX RAW CARDS REPOSITORY'],
        ['DATA INTEGRITY', 'VERIFIED  •  NO SILENT SUBSTITUTION'],
      ];

      rows.forEach(([k, v], idx) => {
        const ry = dy0 + 80 + idx * 56;
        ctx.fillStyle = '#718096';
        ctx.font = '14px monospace';
        ctx.fillText(k, dx0 + 30, ry);
        ctx.fillStyle = '#e6fffa';
        ctx.font = 'bold 18px monospace';
        ctx.fillText(v, dx0 + 30, ry + 24);
        ctx.strokeStyle = '#1a3644';
        ctx.beginPath();
        ctx.moveTo(dx0 + 30, ry + 36);
        ctx.lineTo(dx0 + dw - 30, ry + 36);
        ctx.stroke();
      });

      // Responsive acquisition matrix table in right panel
      const tableY = dy0 + 440;
      ctx.fillStyle = '#4fd1c5';
      ctx.font = 'bold 16px monospace';
      ctx.fillText(`PLAYER ACQUISITION MATRIX // ${players.length} SLOTS`, dx0 + 30, tableY);

      const tableContainer = {
        x: dx0 + 30,
        y: tableY + 16,
        width: dw - 60,
        height: dh - (tableY - dy0) - 36,
      };
      const dossierSlots = computePlayerSlotLayout(players.length, tableContainer, 'vertical', 6);

      players.forEach((p: any, idx: number) => {
        const slot = dossierSlots[idx];
        if (!slot) return;
        const { x: sx, y: sy, width: sw, height: sh } = slot.bounds;
        const owned = p.status === 'confirmed_owned' || p.own === true;
        ctx.fillStyle = owned ? '#1d4044' : '#141a22';
        ctx.fillRect(sx, sy, sw, sh);
        ctx.strokeStyle = owned ? '#319795' : '#2d3748';
        ctx.strokeRect(sx, sy, sw, sh);

        ctx.fillStyle = owned ? '#81e6d9' : '#718096';
        ctx.font = 'bold 14px monospace';
        const pid = p.player_id || `P${idx + 1}`;
        const dName = p.display_name ? ` (${p.display_name})` : '';
        ctx.fillText(`${pid}${dName}`, sx + 12, sy + sh / 2 + 5);

        ctx.font = '13px monospace';
        if (owned) {
          ctx.fillStyle = '#b2f5ea';
          ctx.fillText(`OWNED  •  E${p.elite ?? 2} LV.${p.level ?? 60} POT.${p.potential ?? 1}`, sx + 170, sy + sh / 2 + 5);
        } else {
          ctx.fillStyle = '#4a5568';
          ctx.fillText('UNOWNED // NO DATA', sx + 170, sy + sh / 2 + 5);
        }
      });

    } else {
      // --- MODE C: METADATA-ONLY FALLBACK ---
      const mw = 880;
      const mh = 660;
      const mx0 = cx - mw / 2;
      const my0 = cy - mh / 2;

      ctx.fillStyle = 'rgba(7, 20, 28, 0.94)';
      ctx.fillRect(mx0, my0, mw, mh);
      ctx.strokeStyle = '#285e61';
      ctx.lineWidth = 2;
      ctx.strokeRect(mx0, my0, mw, mh);
      drawCornerReticles(ctx, mx0, my0, mw, mh, 16, '#e2e8f0');

      ctx.fillStyle = '#e2e8f0';
      ctx.font = 'bold 36px monospace';
      ctx.fillText(`TELEMETRY DOSSIER // ${op.operator_name}`, mx0 + 40, my0 + 70);

      ctx.fillStyle = '#a0aec0';
      ctx.font = '20px monospace';
      ctx.fillText(`OPERATOR ID: ${op.operator_id}   •   STATUS: RECORD ACTIVE (METADATA ONLY)`, mx0 + 40, my0 + 110);
    }

    // Reset alpha after panel rendering
    ctx.globalAlpha = 1.0;

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
