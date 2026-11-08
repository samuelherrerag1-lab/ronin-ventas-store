import React, { useMemo, useState } from 'react';
import { useSize } from '../../hooks/useUi';
import { compact, dayLabel, num, usd } from '../../utils/format';
import type { DayPoint, SeriesKey } from './metricsModel';

interface Props {
  points: DayPoint[];
  metric: SeriesKey;
  area: boolean;
  height?: number;
}

const PAD = { top: 14, right: 10, bottom: 22, left: 46 };

const METRIC_LABEL: Record<string, string> = {
  impressions: 'Impresiones',
  clicks: 'Clics',
  revenue: 'Ingresos',
  sales: 'Ventas',
  saves: 'Saves',
};

const niceMax = (value: number): number => {
  if (value <= 0) return 1;
  const pow = Math.pow(10, Math.floor(Math.log10(value)));
  const n = value / pow;
  const step = n <= 1 ? 1 : n <= 2 ? 2 : n <= 5 ? 5 : 10;
  return step * pow;
};

const fmt = (key: SeriesKey, value: number): string =>
  key === 'revenue' ? usd(value, value < 100 ? 2 : 0) : compact(value);

/**
 * Serie diaria con crosshair, tooltip y navegación por teclado.
 * Coordenadas en px reales (ResizeObserver) para que el texto no se deforme.
 */
export const TrendChart: React.FC<Props> = ({ points, metric, area, height = 208 }) => {
  const [ref, size] = useSize<HTMLDivElement>();
  const [hover, setHover] = useState<number | null>(null);

  const values = useMemo(() => points.map((p) => p[metric]), [points, metric]);
  const max = niceMax(Math.max(1, ...values));
  const w = Math.max(280, size.w);
  const plotW = w - PAD.left - PAD.right;
  const plotH = height - PAD.top - PAD.bottom;
  const stepX = points.length > 1 ? plotW / (points.length - 1) : plotW;

  const x = (i: number) => PAD.left + i * stepX;
  const y = (v: number) => PAD.top + plotH - (v / max) * plotH;

  const line = values.map((v, i) => `${i === 0 ? 'M' : 'L'}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(' ');
  const areaPath = `${line} L${x(values.length - 1).toFixed(1)},${PAD.top + plotH} L${PAD.left},${PAD.top + plotH} Z`;

  const ticks = [0, 0.25, 0.5, 0.75, 1];
  const xTickIdx = points.length > 1 ? [0, Math.round((points.length - 1) * 0.25), Math.round((points.length - 1) * 0.5), Math.round((points.length - 1) * 0.75), points.length - 1] : [0];

  const onMove = (event: React.PointerEvent<HTMLDivElement>) => {
    const rect = event.currentTarget.getBoundingClientRect();
    const rel = event.clientX - rect.left - PAD.left;
    const index = Math.round(rel / Math.max(1, stepX));
    setHover(Math.min(points.length - 1, Math.max(0, index)));
  };

  const onKey = (event: React.KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
      event.preventDefault();
      setHover((current) => {
        const next = (current ?? 0) + (event.key === 'ArrowRight' ? 1 : -1);
        return Math.min(points.length - 1, Math.max(0, next));
      });
    }
  };

  const active = hover !== null ? points[hover] : null;
  const activeValue = hover !== null ? values[hover] : 0;

  return (
    <div className="relative" ref={ref}>
      <div
        role="img"
        tabIndex={0}
        aria-label={`Serie diaria de ${METRIC_LABEL[metric].toLowerCase()} en los últimos ${points.length} días. Usa las flechas para recorrer los puntos.`}
        className="relative w-full cursor-crosshair outline-none focus-visible:ring-1 focus-visible:ring-accent/60"
        style={{ height }}
        onPointerMove={onMove}
        onPointerLeave={() => setHover(null)}
        onKeyDown={onKey}
        onBlur={() => setHover(null)}
      >
        <svg width="100%" height={height} viewBox={`0 0 ${w} ${height}`} preserveAspectRatio="none" aria-hidden="true">
          {ticks.map((t) => {
            const gy = PAD.top + plotH - t * plotH;
            return <line key={t} x1={PAD.left} x2={w - PAD.right} y1={gy} y2={gy} stroke="var(--line)" strokeWidth="1" />;
          })}
          {ticks.map((t) => (
            <text key={`y${t}`} x={PAD.left - 8} y={PAD.top + plotH - t * plotH + 3} textAnchor="end" fontSize="10" fill="var(--ink-3)">
              {fmt(metric, max * t)}
            </text>
          ))}
          {xTickIdx.map((i, k) => (
            <text
              key={`x${i}`}
              x={x(i)}
              y={height - 6}
              textAnchor={k === 0 ? 'start' : k === xTickIdx.length - 1 ? 'end' : 'middle'}
              fontSize="10"
              fill="var(--ink-3)"
            >
              {dayLabel(points[i]?.date ?? '')}
            </text>
          ))}
          {area && <path d={areaPath} fill="var(--accent)" opacity="0.10" />}
          <path d={line} fill="none" stroke="var(--accent)" strokeWidth="1.8" strokeLinejoin="round" strokeLinecap="round" />
          <line x1={PAD.left} x2={w - PAD.right} y1={PAD.top + plotH} y2={PAD.top + plotH} stroke="var(--line-2)" strokeWidth="1" />
          {hover !== null && (
            <>
              <line x1={x(hover)} x2={x(hover)} y1={PAD.top} y2={PAD.top + plotH} stroke="var(--line-2)" strokeWidth="1" strokeDasharray="3 3" />
              <circle cx={x(hover)} cy={y(values[hover] ?? 0)} r="3.4" fill="var(--accent)" stroke="var(--bg)" strokeWidth="2" />
            </>
          )}
        </svg>

        {active && (
          <div
            className="animate-tooltip pointer-events-none absolute z-10 min-w-[124px] rounded-md border border-line2 bg-[#17171c] px-2.5 py-1.5 shadow-[0_12px_30px_rgba(0,0,0,0.65)]"
            style={{
              left: Math.min(Math.max(0, x(hover ?? 0) - 62), w - 140),
              top: PAD.top + 4,
            }}
          >
            <p className="text-[10px] text-ink3">{dayLabel(active.date)}</p>
            <p className="num mt-0.5 text-[12.5px] text-ink">
              {fmt(metric, activeValue)}
              <span className="ml-1 text-[10px] font-normal text-ink3">{METRIC_LABEL[metric].toLowerCase()}</span>
            </p>
          </div>
        )}
      </div>
      <p className="mt-1 text-[10px] text-ink3 sm:hidden">Toca o usa ← → para recorrer la serie</p>
    </div>
  );
};
