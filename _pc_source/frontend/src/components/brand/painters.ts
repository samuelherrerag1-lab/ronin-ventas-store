/** Variantes cuadradas y orquestador del canvas. Nada se sube a un servidor. */

import type { VariantId } from './brandSpecs';
import { VARIANTS } from './brandSpecs';
import { DISPLAY, INK, MONO, circleClip, drawCover, fillRect, roundedPath, setFont } from './drawing';
import type { Ctx } from './drawing';
import { paintBanner, paintOpenGraph, paintPin } from './painters-wide';
import type { PaintOptions } from './paintShared';

export type { PaintOptions } from './paintShared';

function paintAvatar(ctx: Ctx, image: HTMLImageElement, options: PaintOptions): void {
  const size = 512;
  fillRect(ctx, options.background.hex, 0, 0, size, size);
  const radius = size / 2 - 10;
  ctx.save();
  circleClip(ctx, size / 2, size / 2, radius);
  drawCover(ctx, image, 10, 10, size - 20, size - 20, options.zoom);
  ctx.restore();
  ctx.strokeStyle = options.background.ring;
  ctx.lineWidth = 8;
  ctx.beginPath();
  ctx.arc(size / 2, size / 2, radius, 0, Math.PI * 2);
  ctx.stroke();
}

function paintFavicon(ctx: Ctx, image: HTMLImageElement, options: PaintOptions): void {
  const size = 64;
  fillRect(ctx, options.background.hex, 0, 0, size, size);
  ctx.save();
  roundedPath(ctx, 0, 0, size, size, 16);
  ctx.clip();
  drawCover(ctx, image, 0, 0, size, size, options.zoom);
  ctx.restore();
  ctx.strokeStyle = 'rgba(255,255,255,0.18)';
  ctx.lineWidth = 2;
  roundedPath(ctx, 1, 1, size - 2, size - 2, 15);
  ctx.stroke();
}

function paintPlaceholder(ctx: Ctx, w: number, h: number, options: PaintOptions): void {
  const small = w <= 200;
  const light = small ? options.background.hex !== '#F5F3EF' : true;
  fillRect(ctx, small ? options.background.hex : INK, 0, 0, w, h);
  const stroke = light ? 'rgba(245,243,239,0.35)' : 'rgba(8,8,12,0.35)';
  const ink = light ? 'rgba(245,243,239,0.6)' : 'rgba(8,8,12,0.55)';

  if (small) {
    const initial = (options.copy.name.trim() || 'R').charAt(0).toUpperCase();
    setFont(ctx, 700, Math.min(w, h) * 0.5, DISPLAY);
    ctx.fillStyle = ink;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(initial, w / 2, h / 2 + 2);
    ctx.textAlign = 'left';
    ctx.textBaseline = 'alphabetic';
    return;
  }

  const cx = w / 2;
  const cy = h / 2 - Math.min(w, h) * 0.06;
  const radius = Math.min(w, h) * 0.16;
  ctx.strokeStyle = stroke;
  ctx.lineWidth = Math.max(2, Math.min(w, h) * 0.004);
  ctx.setLineDash([12, 10]);
  ctx.beginPath();
  ctx.arc(cx, cy, radius, 0, Math.PI * 2);
  ctx.stroke();
  ctx.setLineDash([]);
  setFont(ctx, 500, Math.max(14, Math.min(w, h) * 0.032), MONO);
  ctx.fillStyle = ink;
  ctx.textAlign = 'center';
  ctx.fillText('SUBIR IMAGEN', cx, cy + radius + Math.min(w, h) * 0.07);
  ctx.textAlign = 'left';
}

/** Pinta una variante en el canvas indicado, redimensionándolo al tamaño final. */
export function paintVariant(
  canvas: HTMLCanvasElement,
  image: HTMLImageElement | null,
  id: VariantId,
  options: PaintOptions,
): void {
  const spec = VARIANTS.find((variant) => variant.id === id);
  if (!spec) return;
  canvas.width = spec.width;
  canvas.height = spec.height;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.clearRect(0, 0, spec.width, spec.height);
  ctx.textAlign = 'left';
  ctx.textBaseline = 'alphabetic';

  if (!image || image.naturalWidth === 0 || image.naturalHeight === 0) {
    paintPlaceholder(ctx, spec.width, spec.height, options);
    return;
  }

  switch (id) {
    case 'avatar':
      paintAvatar(ctx, image, options);
      break;
    case 'banner':
      paintBanner(ctx, image, options);
      break;
    case 'og':
      paintOpenGraph(ctx, image, options);
      break;
    case 'pin':
      paintPin(ctx, image, options);
      break;
    case 'favicon':
      paintFavicon(ctx, image, options);
      break;
    default:
      break;
  }
}
