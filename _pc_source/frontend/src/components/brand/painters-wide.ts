/** Variantes anchas: banner de Threads, Open Graph y pin 2:3. */

import { SUITE_LABEL } from './brandSpecs';
import {
  CREAM, DISPLAY, EMERALD, INK, MONO, TERRACOTTA,
  circleClip, drawCover, drawPill, fillRect, fitFont, setFont,
} from './drawing';
import type { Ctx } from './drawing';
import { safeHandle, safeName } from './paintShared';
import type { PaintOptions } from './paintShared';

export function paintBanner(ctx: Ctx, image: HTMLImageElement, options: PaintOptions): void {
  const w = 1500;
  const h = 500;
  fillRect(ctx, INK, 0, 0, w, h);
  drawCover(ctx, image, 0, 0, w, h, options.zoom);

  const horizontal = ctx.createLinearGradient(0, 0, w, 0);
  horizontal.addColorStop(0, 'rgba(8,8,12,0.96)');
  horizontal.addColorStop(0.44, 'rgba(8,8,12,0.80)');
  horizontal.addColorStop(1, 'rgba(8,8,12,0.10)');
  ctx.fillStyle = horizontal;
  ctx.fillRect(0, 0, w, h);

  const bottom = ctx.createLinearGradient(0, h * 0.5, 0, h);
  bottom.addColorStop(0, 'rgba(8,8,12,0)');
  bottom.addColorStop(1, 'rgba(8,8,12,0.78)');
  ctx.fillStyle = bottom;
  ctx.fillRect(0, h * 0.5, w, h * 0.5);

  fillRect(ctx, TERRACOTTA, 0, 0, 6, h);

  const cx = 150;
  const cy = 250;
  const radius = 74;
  ctx.save();
  circleClip(ctx, cx, cy, radius);
  drawCover(ctx, image, cx - radius, cy - radius, radius * 2, radius * 2, options.zoom);
  ctx.restore();
  ctx.strokeStyle = 'rgba(255,255,255,0.32)';
  ctx.lineWidth = 4;
  ctx.beginPath();
  ctx.arc(cx, cy, radius, 0, Math.PI * 2);
  ctx.stroke();

  fitFont(ctx, safeName(options.copy), 980, 700, 56, DISPLAY);
  ctx.fillStyle = CREAM;
  ctx.fillText(safeName(options.copy), 272, 236);

  setFont(ctx, 500, 22, MONO);
  ctx.fillStyle = TERRACOTTA;
  ctx.fillText(safeHandle(options.copy), 274, 282);

  setFont(ctx, 400, 20, DISPLAY);
  ctx.fillStyle = 'rgba(245,243,239,0.74)';
  ctx.fillText(options.copy.tagline, 274, 322);

  const label = 'THREADS · 1500 × 500';
  setFont(ctx, 500, 16, MONO);
  const pillW = ctx.measureText(label).width + 36;
  drawPill(ctx, w - 48 - pillW, 40, label, {
    height: 38, padding: 18, fontSize: 16, weight: 500,
    textColor: 'rgba(245,243,239,0.72)', fillColor: 'rgba(8,8,12,0.62)',
    strokeColor: 'rgba(255,255,255,0.18)',
  });
}

export function paintOpenGraph(ctx: Ctx, image: HTMLImageElement, options: PaintOptions): void {
  const w = 1200;
  const h = 630;
  fillRect(ctx, INK, 0, 0, w, h);
  drawCover(ctx, image, 0, 0, w, h, options.zoom);

  const scrim = ctx.createLinearGradient(0, h * 0.28, 0, h);
  scrim.addColorStop(0, 'rgba(8,8,12,0)');
  scrim.addColorStop(0.55, 'rgba(8,8,12,0.74)');
  scrim.addColorStop(1, 'rgba(8,8,12,0.97)');
  ctx.fillStyle = scrim;
  ctx.fillRect(0, 0, w, h);

  drawPill(ctx, 72, 56, SUITE_LABEL, {
    height: 42, padding: 20, fontSize: 17, weight: 500,
    textColor: 'rgba(245,243,239,0.8)', fillColor: 'rgba(8,8,12,0.55)',
    strokeColor: 'rgba(255,255,255,0.22)',
  });

  fillRect(ctx, TERRACOTTA, 72, 392, 6, 142);

  fitFont(ctx, safeName(options.copy), 960, 700, 68, DISPLAY);
  ctx.fillStyle = CREAM;
  ctx.fillText(safeName(options.copy), 104, 452);

  setFont(ctx, 500, 26, MONO);
  ctx.fillStyle = TERRACOTTA;
  ctx.fillText(safeHandle(options.copy), 106, 504);

  setFont(ctx, 400, 24, DISPLAY);
  ctx.fillStyle = 'rgba(245,243,239,0.76)';
  ctx.fillText(options.copy.tagline, 106, 546);

  setFont(ctx, 500, 16, MONO);
  ctx.fillStyle = 'rgba(245,243,239,0.45)';
  ctx.textAlign = 'right';
  ctx.fillText('OG · 1200 × 630', w - 72, 596);
  ctx.textAlign = 'left';
}

export function paintPin(ctx: Ctx, image: HTMLImageElement, options: PaintOptions): void {
  const w = 1000;
  const h = 1500;
  fillRect(ctx, INK, 0, 0, w, h);
  drawCover(ctx, image, 0, 0, w, h, options.zoom);

  const scrim = ctx.createLinearGradient(0, h * 0.34, 0, h);
  scrim.addColorStop(0, 'rgba(8,8,12,0)');
  scrim.addColorStop(0.5, 'rgba(8,8,12,0.68)');
  scrim.addColorStop(1, 'rgba(8,8,12,0.98)');
  ctx.fillStyle = scrim;
  ctx.fillRect(0, h * 0.34, w, h * 0.66);

  drawPill(ctx, 64, 72, 'IDENTIDAD DE MARCA', {
    height: 46, padding: 22, fontSize: 18, weight: 500,
    textColor: 'rgba(245,243,239,0.86)', fillColor: 'rgba(8,8,12,0.68)',
    strokeColor: 'rgba(255,255,255,0.2)',
  });

  ctx.fillStyle = EMERALD;
  ctx.beginPath();
  ctx.arc(72, 1122, 5, 0, Math.PI * 2);
  ctx.fill();
  setFont(ctx, 500, 18, MONO);
  ctx.fillStyle = 'rgba(245,243,239,0.58)';
  ctx.fillText('EL INSIDER CÍNICO', 88, 1128);

  fitFont(ctx, safeName(options.copy), 872, 700, 96, DISPLAY);
  ctx.fillStyle = CREAM;
  ctx.fillText(safeName(options.copy), 64, 1218);

  setFont(ctx, 500, 30, MONO);
  ctx.fillStyle = TERRACOTTA;
  ctx.fillText(safeHandle(options.copy), 66, 1272);

  fillRect(ctx, TERRACOTTA, 64, 1304, 96, 4);

  setFont(ctx, 400, 26, DISPLAY);
  ctx.fillStyle = 'rgba(245,243,239,0.78)';
  ctx.fillText(options.copy.tagline, 64, 1358);

  setFont(ctx, 500, 16, MONO);
  ctx.fillStyle = 'rgba(245,243,239,0.45)';
  ctx.fillText(SUITE_LABEL, 64, 1432);
  ctx.textAlign = 'right';
  ctx.fillText('PIN · 1000 × 1500', w - 64, 1432);
  ctx.textAlign = 'left';
}
