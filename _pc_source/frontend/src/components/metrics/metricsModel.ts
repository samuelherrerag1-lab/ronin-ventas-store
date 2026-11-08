import type { MetricsRealState, MetricsSummaryResponse, PerformancePiece } from '../../types/domain';
import { clamp, distribute, lastDays } from '../../utils/format';

export type PlatformFilter = 'all' | 'threads' | 'pinterest';
export type SeriesKey = 'impressions' | 'clicks' | 'saves' | 'revenue' | 'sales';

export interface DayPoint {
  date: string;
  impressions: number;
  clicks: number;
  saves: number;
  revenue: number;
  sales: number;
}

export interface Totals {
  impressions: number;
  clicks: number;
  saves: number;
  revenue: number;
  sales: number;
  ctr: number | null;
}

export type Verdict = 'DOBLAR' | 'MATAR' | 'MUTAR' | 'OBSERVACION';

export interface PieceRow {
  piece_id: string;
  platform: string;
  sku_id: string | null;
  route: string | null;
  impressions: number;
  clicks: number;
  saves: number;
  ctr: number;
  verdict: Verdict;
  reason: string;
  revenue: number | null;
}

/** Pesos deterministas (sin Math.random) para que la demo no cambie entre renders. */
const demoWeight = (i: number, seed: number, span: number): number => {
  const trend = 0.85 + 0.9 * (i / Math.max(1, span - 1));
  const wave = 0.5 * Math.sin((i + seed) * 0.72) + 0.28 * Math.cos((i + seed) * 1.7);
  const spike = i === Math.round(span * 0.68) ? 0.55 : 0;
  return Math.max(0.15, trend + wave + spike);
};

export const sumSeries = (points: DayPoint[]): Totals => {
  const base = points.reduce(
    (acc, p) => ({
      impressions: acc.impressions + p.impressions,
      clicks: acc.clicks + p.clicks,
      saves: acc.saves + p.saves,
      revenue: acc.revenue + p.revenue,
      sales: acc.sales + p.sales,
    }),
    { impressions: 0, clicks: 0, saves: 0, revenue: 0, sales: 0 },
  );
  return { ...base, ctr: base.impressions > 0 ? (base.clicks / base.impressions) * 100 : null };
};

/**
 * Serie diaria. Con datos reales se agrupa `/api/metrics/raw` por fecha; en modo
 * demo se reparte cada total entre los días de forma que la suma sea exacta.
 * Sin datos reales y sin demo devuelve vacío: la vista muestra su estado honesto.
 */
export const buildSeries = (
  raw: MetricsRealState | null,
  demo: boolean,
  summary: MetricsSummaryResponse | null,
  windowDays: number,
): DayPoint[] => {
  const days = lastDays(windowDays);
  if (demo && summary) {
    const weightsFor = (seed: number) => days.map((_, i) => demoWeight(i, seed, days.length));
    const impressions = distribute(summary.total_impressions, weightsFor(3));
    const clicks = distribute(summary.total_clicks, weightsFor(9));
    const saves = distribute(summary.total_saves, weightsFor(14));
    const sales = distribute(summary.total_sales, weightsFor(18));
    const cents = distribute(Math.round(summary.total_revenue_usd * 100), weightsFor(24));
    return days.map((date, i) => ({
      date,
      impressions: impressions[i],
      clicks: clicks[i],
      saves: saves[i],
      sales: sales[i],
      revenue: cents[i] / 100,
    }));
  }
  if (!raw) return [];
  const byDate = new Map<string, DayPoint>(days.map((date) => [date, { date, impressions: 0, clicks: 0, saves: 0, revenue: 0, sales: 0 }]));
  raw.manual_piece_metrics.forEach((row) => {
    const point = byDate.get(row.date.slice(0, 10));
    if (!point) return;
    point.impressions += row.impressions;
    point.clicks += row.clicks;
    point.saves += row.saves;
  });
  raw.sales.forEach((sale) => {
    const point = byDate.get(sale.date.slice(0, 10));
    if (!point) return;
    point.revenue += sale.amount_usd;
    point.sales += 1;
  });
  return [...byDate.values()];
};

export const verdictTone = (verdict: Verdict): 'pos' | 'neg' | 'warn' | 'mute' =>
  verdict === 'DOBLAR' ? 'pos' : verdict === 'MATAR' ? 'neg' : verdict === 'MUTAR' ? 'warn' : 'mute';

const verdictOf = (ctr: number): Verdict => (ctr >= 2 ? 'DOBLAR' : ctr < 0.8 ? 'MATAR' : 'OBSERVACION');

const toneOfPiece = (piece: PerformancePiece): Verdict => (piece.verdict as Verdict) ?? verdictOf(piece.ctr_percent);

/** Filas de la tabla: crudas si existen, si no el agregado que ya calcula el backend. */
export const buildPieces = (summary: MetricsSummaryResponse | null, raw: MetricsRealState | null): PieceRow[] => {
  if (raw && raw.manual_piece_metrics.length > 0) {
    const map = new Map<string, PieceRow>();
    raw.manual_piece_metrics.forEach((row) => {
      const key = `${row.platform}:${row.piece_id}`;
      const current = map.get(key);
      const impressions = (current?.impressions ?? 0) + row.impressions;
      const clicks = (current?.clicks ?? 0) + row.clicks;
      const saves = (current?.saves ?? 0) + row.saves;
      const ctr = impressions > 0 ? (clicks / impressions) * 100 : 0;
      map.set(key, {
        piece_id: row.piece_id,
        platform: row.platform,
        sku_id: row.sku_id ?? current?.sku_id ?? null,
        route: row.route ?? current?.route ?? null,
        impressions,
        clicks,
        saves,
        ctr,
        verdict: verdictOf(ctr),
        reason: row.notes ?? 'Registro manual de pieza.',
        revenue: null,
      });
    });
    return [...map.values()].sort((a, b) => b.impressions - a.impressions);
  }
  if (!summary) return [];
  return [...summary.winning_pieces, ...summary.losing_pieces]
    .map((piece) => ({
      piece_id: piece.piece_id,
      platform: piece.platform,
      sku_id: piece.sku_id ?? null,
      route: piece.route ?? null,
      impressions: piece.impressions,
      clicks: piece.clicks,
      saves: piece.saves,
      ctr: piece.ctr_percent,
      verdict: toneOfPiece(piece),
      reason: piece.reason,
      revenue: null,
    }))
    .sort((a, b) => b.impressions - a.impressions);
};

export const filterPieces = (rows: PieceRow[], platform: PlatformFilter, sku: string): PieceRow[] =>
  rows.filter((row) => (platform === 'all' || row.platform === platform) && (sku === 'all' || row.sku_id === sku));

export const sparkFor = (points: DayPoint[], key: SeriesKey): number[] => points.map((p) => p[key]);

/* ---------- What-if ---------- */
export interface WhatIfBase {
  impressions: number;
  ctr: number;
  closeRate: number;
  price: number;
}

export interface WhatIfResult {
  clicks: number;
  sales: number;
  revenue: number;
}

export const whatIfBase = (summary: MetricsSummaryResponse | null): WhatIfBase | null => {
  if (!summary || summary.total_impressions <= 0) return null;
  const ctr = summary.ctr_percent ?? (summary.total_clicks / summary.total_impressions) * 100;
  const closeRate = summary.total_clicks > 0 ? summary.total_sales / summary.total_clicks : 0;
  const price = summary.aov_usd ?? summary.total_revenue_usd / Math.max(1, summary.total_sales);
  return { impressions: summary.total_impressions, ctr, closeRate, price };
};

export const projectWhatIf = (
  base: WhatIfBase,
  knobs: { ctrLift: number; closeLift: number; priceLift: number },
): WhatIfResult => {
  const ctr = clamp(base.ctr * (1 + knobs.ctrLift / 100), 0, 100);
  const closeRate = clamp(base.closeRate * (1 + knobs.closeLift / 100), 0, 1);
  const price = Math.max(0, base.price * (1 + knobs.priceLift / 100));
  const clicks = (base.impressions * ctr) / 100;
  const sales = clicks * closeRate;
  return { clicks, sales, revenue: sales * price };
};
