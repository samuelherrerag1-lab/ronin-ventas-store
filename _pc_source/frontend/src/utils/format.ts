/** Formato único de cifras: separadores es-CO, decimales fijos por métrica. */

const int = new Intl.NumberFormat('es-CO', { maximumFractionDigits: 0 });
const dec1 = new Intl.NumberFormat('es-CO', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const dec2 = new Intl.NumberFormat('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

export const num = (value: number | null | undefined, digits = 0): string => {
  if (value === null || value === undefined || !Number.isFinite(value)) return '—';
  if (digits === 2) return dec2.format(value);
  if (digits === 1) return dec1.format(value);
  return int.format(value);
};

export const usd = (value: number | null | undefined, digits = 2): string =>
  value === null || value === undefined || !Number.isFinite(value) ? '—' : `$${num(value, digits)}`;

/** 18.450 → "18,4k" · 1.240.000 → "1,2M" (solo para capacidad o ejes). */
export const compact = (value: number | null | undefined): string => {
  if (value === null || value === undefined || !Number.isFinite(value)) return '—';
  const abs = Math.abs(value);
  if (abs >= 1_000_000) return `${dec1.format(value / 1_000_000)}M`;
  if (abs >= 10_000) return `${dec1.format(value / 1_000)}k`;
  return int.format(value);
};

export const pct = (value: number | null | undefined, digits = 1): string =>
  value === null || value === undefined || !Number.isFinite(value) ? '—' : `${num(value, digits)}%`;

export const signed = (value: number | null | undefined, digits = 1, suffix = '%'): string => {
  if (value === null || value === undefined || !Number.isFinite(value)) return '—';
  const sign = value > 0 ? '+' : value < 0 ? '−' : '±';
  return `${sign}${num(Math.abs(value), digits)}${suffix}`;
};

export const clamp = (value: number, min: number, max: number): number =>
  Math.min(max, Math.max(min, value));

/** Ratio seguro para barras y ejes: nunca NaN, nunca división por cero. */
export const ratio = (part: number, whole: number): number => (whole > 0 ? clamp(part / whole, 0, 1) : 0);

/** Reparte un total en N partes con pesos, garantizando que la suma sea exacta. */
export const distribute = (total: number, weights: number[]): number[] => {
  const sum = weights.reduce((acc, w) => acc + Math.max(0, w), 0) || 1;
  const raw = weights.map((w) => (Math.max(0, w) / sum) * total);
  const floors = raw.map((v) => Math.floor(v));
  let rest = Math.round(total) - floors.reduce((acc, v) => acc + v, 0);
  const order = raw.map((v, i) => ({ i, frac: v - Math.floor(v) })).sort((a, b) => b.frac - a.frac);
  const out = [...floors];
  for (let k = 0; k < order.length && rest > 0; k += 1) {
    out[order[k].i] += 1;
    rest -= 1;
  }
  return out;
};

export const dayLabel = (iso: string): string => {
  const date = new Date(`${iso}T12:00:00`);
  return date.toLocaleDateString('es-CO', { day: '2-digit', month: 'short' }).replace('.', '');
};

export const shortDate = (iso: string): string => {
  const date = new Date(iso.length <= 10 ? `${iso}T12:00:00` : iso);
  if (Number.isNaN(date.getTime())) return iso;
  return date.toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: '2-digit' }).replace('.', '');
};

export const timeAgo = (iso: string | null | undefined): string => {
  if (!iso) return 'sin sincronizar';
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return 'sin sincronizar';
  const mins = Math.round((Date.now() - then) / 60000);
  if (mins < 1) return 'ahora';
  if (mins < 60) return `hace ${mins} min`;
  const hours = Math.round(mins / 60);
  if (hours < 24) return `hace ${hours} h`;
  return `hace ${Math.round(hours / 24)} d`;
};

const isoLocal = (d: Date): string =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;

export const lastDays = (days: number): string[] => {
  const out: string[] = [];
  const today = new Date();
  for (let i = days - 1; i >= 0; i -= 1) {
    const d = new Date(today);
    d.setDate(today.getDate() - i);
    out.push(isoLocal(d));
  }
  return out;
};
