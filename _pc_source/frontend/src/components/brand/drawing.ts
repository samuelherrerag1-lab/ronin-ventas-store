/** Primitivas de dibujo compartidas por los cinco formatos. */

export const INK = '#08080C';
export const CREAM = '#F5F3EF';
export const TERRACOTTA = '#E07A5F';
export const EMERALD = '#10B981';
export const DISPLAY = '"Bricolage Grotesque Variable", "Bricolage Grotesque", ui-sans-serif, sans-serif';
export const MONO = '"Martian Mono", ui-monospace, SFMono-Regular, monospace';

export type Ctx = CanvasRenderingContext2D;

export function fillRect(ctx: Ctx, color: string, x: number, y: number, w: number, h: number): void {
  ctx.fillStyle = color;
  ctx.fillRect(x, y, w, h);
}

/** Recorte "cover" centrado con zoom >= 1. */
export function drawCover(ctx: Ctx, image: HTMLImageElement, x: number, y: number, w: number, h: number, zoom: number): void {
  const iw = image.naturalWidth;
  const ih = image.naturalHeight;
  if (!iw || !ih) return;
  const scale = Math.max(w / iw, h / ih) * Math.max(1, zoom);
  const dw = iw * scale;
  const dh = ih * scale;
  ctx.drawImage(image, x + (w - dw) / 2, y + (h - dh) / 2, dw, dh);
}

export function circleClip(ctx: Ctx, cx: number, cy: number, radius: number): void {
  ctx.beginPath();
  ctx.arc(cx, cy, radius, 0, Math.PI * 2);
  ctx.clip();
}

export function roundedPath(ctx: Ctx, x: number, y: number, w: number, h: number, radius: number): void {
  const r = Math.max(0, Math.min(radius, w / 2, h / 2));
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

export function setFont(ctx: Ctx, weight: number, size: number, family: string): void {
  ctx.font = `${weight} ${Math.max(1, Math.round(size))}px ${family}`;
}

/** Ajusta el tamaño tipográfico hasta que el texto entre en maxWidth. */
export function fitFont(ctx: Ctx, value: string, maxWidth: number, weight: number, size: number, family: string): number {
  let current = size;
  setFont(ctx, weight, current, family);
  while (current > 14 && ctx.measureText(value).width > maxWidth) {
    current -= 2;
    setFont(ctx, weight, current, family);
  }
  return current;
}

export interface PillOptions {
  height: number;
  padding: number;
  fontSize: number;
  weight?: number;
  textColor: string;
  fillColor: string;
  strokeColor?: string;
  family?: string;
}

/** Devuelve el ancho dibujado para poder alinear a la derecha. */
export function drawPill(ctx: Ctx, x: number, y: number, label: string, options: PillOptions): number {
  const family = options.family ?? MONO;
  setFont(ctx, options.weight ?? 600, options.fontSize, family);
  const width = ctx.measureText(label).width + options.padding * 2;
  roundedPath(ctx, x, y, width, options.height, options.height / 2);
  ctx.fillStyle = options.fillColor;
  ctx.fill();
  if (options.strokeColor) {
    ctx.strokeStyle = options.strokeColor;
    ctx.lineWidth = 1.5;
    ctx.stroke();
  }
  ctx.fillStyle = options.textColor;
  const previousBaseline = ctx.textBaseline;
  ctx.textBaseline = 'middle';
  ctx.fillText(label, x + options.padding, y + options.height / 2 + 1);
  ctx.textBaseline = previousBaseline;
  return width;
}
