import React, { useMemo, useState } from 'react';
import { Icon } from '../ui/Icon';
import { Panel, PanelHead } from '../ui/primitives';
import { num, pct, ratio } from '../../utils/format';
import type { PieceRow } from './metricsModel';

interface RouteAgg {
  route: string;
  impressions: number;
  clicks: number;
  saves: number;
  ctr: number;
}

const ROWS = [
  { key: 'clicks', label: 'Clics' },
  { key: 'impressions', label: 'Impr.' },
  { key: 'ctr', label: 'CTR' },
] as const;

/** Comparador de dos rutas puente con barras espejadas desde el centro. */
export const RouteComparePanel: React.FC<{ rows: PieceRow[] }> = ({ rows }) => {
  const routes = useMemo<RouteAgg[]>(() => {
    const map = new Map<string, RouteAgg>();
    rows.forEach((row) => {
      if (!row.route) return;
      const agg = map.get(row.route) ?? { route: row.route, impressions: 0, clicks: 0, saves: 0, ctr: 0 };
      agg.impressions += row.impressions;
      agg.clicks += row.clicks;
      agg.saves += row.saves;
      agg.ctr = agg.impressions > 0 ? (agg.clicks / agg.impressions) * 100 : 0;
      map.set(row.route, agg);
    });
    return [...map.values()].sort((a, b) => b.clicks - a.clicks);
  }, [rows]);

  const [left, setLeft] = useState(0);
  const [right, setRight] = useState(1);
  const a = routes[Math.min(left, Math.max(0, routes.length - 1))];
  const b = routes[Math.min(right, Math.max(0, routes.length - 1))];

  return (
    <Panel className="flex flex-col">
      <PanelHead title="Comparador de rutas" icon="route" hint={`${routes.length} rutas con datos`} />
      <div className="p-3.5">
        {routes.length < 2 || !a || !b ? (
          <div className="flex items-center gap-2.5 py-2 text-[11.5px] text-ink3">
            <Icon name="route" size={15} />
            Se necesitan al menos dos rutas con clics registrados para comparar.
          </div>
        ) : (
          <>
            <div className="grid grid-cols-2 gap-2">
              <label className="flex flex-col gap-1">
                <span className="text-[9.5px] text-ink3">Ruta A</span>
                <select className="field w-full" value={left} onChange={(event) => setLeft(Number(event.target.value))} aria-label="Ruta A">
                  {routes.map((route, index) => (
                    <option key={route.route} value={index}>{route.route.replace(/^\//, '')}</option>
                  ))}
                </select>
              </label>
              <label className="flex flex-col gap-1">
                <span className="text-[9.5px] text-ink3">Ruta B</span>
                <select className="field w-full" value={right} onChange={(event) => setRight(Number(event.target.value))} aria-label="Ruta B">
                  {routes.map((route, index) => (
                    <option key={route.route} value={index}>{route.route.replace(/^\//, '')}</option>
                  ))}
                </select>
              </label>
            </div>

            <div className="mt-3 space-y-2">
              {ROWS.map((row) => {
                const max = Math.max(1, a[row.key], b[row.key]);
                const fmt = (value: number) => (row.key === 'ctr' ? pct(value, 2) : num(value));
                return (
                  <div key={row.key} className="grid grid-cols-[1fr_64px_1fr] items-center gap-1.5">
                    <div className="flex items-center justify-end gap-1.5">
                      <span className="num text-[10.5px] text-ink">{fmt(a[row.key])}</span>
                      <span className="flex h-[4px] flex-1 justify-end overflow-hidden rounded-full bg-[#16161b]">
                        <span className="block h-full rounded-full bg-accent/80" style={{ width: `${ratio(a[row.key], max) * 100}%` }} />
                      </span>
                    </div>
                    <span className="text-center text-[9.5px] text-ink3">{row.label}</span>
                    <div className="flex items-center gap-1.5">
                      <span className="flex h-[4px] flex-1 overflow-hidden rounded-full bg-[#16161b]">
                        <span className="block h-full rounded-full bg-[#5d5d6a]" style={{ width: `${ratio(b[row.key], max) * 100}%` }} />
                      </span>
                      <span className="num text-[10.5px] text-ink2">{fmt(b[row.key])}</span>
                    </div>
                  </div>
                );
              })}
            </div>
            <p className="mt-2.5 flex items-center justify-between gap-2 border-t border-line pt-2 text-[9.5px] text-ink3">
              <span>
                {a.clicks > 0 && b.clicks > 0
                  ? `A rinde ${(a.clicks / b.clicks).toFixed(1)}× los clics de B${b.ctr > 0 ? ` y ${(a.ctr / b.ctr).toFixed(1)}× su CTR` : ''}`
                  : 'Sin base suficiente para comparar'}
              </span>
              <span className="shrink-0">ingresos por ruta: pendiente en backend</span>
            </p>
          </>
        )}
      </div>
    </Panel>
  );
};
