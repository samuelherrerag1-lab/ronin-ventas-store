import type { PieceRow } from '../metrics/metricsModel';

export interface RouteRow {
  route: string;
  clicks: number;
  impressions: number;
  saves: number;
  ctr: number;
  platform: string;
}

/** Variación porcentual entre la primera y la segunda mitad de la serie. */
export const halfDelta = (values: number[]): number | null => {
  if (values.length < 4) return null;
  const mid = Math.floor(values.length / 2);
  const prior = values.slice(0, mid).reduce((a, b) => a + b, 0);
  const recent = values.slice(mid).reduce((a, b) => a + b, 0);
  if (prior <= 0) return null;
  return ((recent - prior) / prior) * 100;
};

export const pctOf = (part: number, whole: number): number | null => (whole > 0 ? (part / whole) * 100 : null);

/** Agrupa las piezas con ruta por click descendente (máximo 5 filas). */
export const buildRoutes = (pieces: PieceRow[]): RouteRow[] => {
  const routeMap = new Map<string, RouteRow>();
  pieces.forEach((piece) => {
    if (!piece.route) return;
    const row = routeMap.get(piece.route) ?? {
      route: piece.route,
      clicks: 0,
      impressions: 0,
      saves: 0,
      ctr: 0,
      platform: piece.platform,
    };
    row.clicks += piece.clicks;
    row.impressions += piece.impressions;
    row.saves += piece.saves;
    row.ctr = row.impressions > 0 ? (row.clicks / row.impressions) * 100 : 0;
    routeMap.set(piece.route, row);
  });
  return [...routeMap.values()].sort((a, b) => b.clicks - a.clicks).slice(0, 5);
};
