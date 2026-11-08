import React from 'react';
import { CountUp } from '../ui/CountUp';
import { Icon } from '../ui/Icon';
import { Delta } from '../ui/primitives';
import { Sparkline } from '../ui/Sparkline';
import { Tip } from '../ui/Tooltip';
import type { KpiDef } from './useHomeModel';

interface Props {
  kpis: KpiDef[];
  loading: boolean;
}

const Value: React.FC<{ kpi: KpiDef }> = ({ kpi }) => {
  if (kpi.value === null || kpi.value === undefined) {
    return <span className="text-[13px] text-ink3">sin datos</span>;
  }
  if (kpi.format === 'usd') {
    return (
      <span className="flex items-baseline">
        <span className="mr-0.5 text-[17px] leading-none text-ink3">$</span>
        <CountUp value={kpi.value} digits={2} className="metric-xl num text-ink" />
        <span className="unit">USD</span>
      </span>
    );
  }
  if (kpi.format === 'pct') {
    return (
      <span className="flex items-baseline">
        <CountUp value={kpi.value} digits={1} className="metric-xl num text-ink" />
        <span className="ml-0.5 text-[15px] leading-none text-ink3">%</span>
      </span>
    );
  }
  return <CountUp value={kpi.value} className="metric-xl num text-ink" />;
};

/** Cuatro cifras del negocio; la serie diaria de cada una va dibujada a mano. */
export const KpiGrid: React.FC<Props> = ({ kpis, loading }) => {
  if (loading && kpis.every((k) => k.value === null)) {
    return (
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4 lg:gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="panel h-[124px] p-4" aria-hidden="true">
            <div className="skel h-2.5 w-16" />
            <div className="skel mt-4 h-6 w-24" />
            <div className="skel mt-4 h-4 w-full" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-4 lg:gap-4">
      {kpis.map((kpi) => {
        const good = kpi.delta === null ? undefined : kpi.goodDirection === 'up' ? kpi.delta >= 0 : kpi.delta <= 0;
        return (
          <article key={kpi.key} className="panel flex min-h-[124px] flex-col px-3.5 pb-2.5 pt-3">
            <div className="flex items-start justify-between gap-2">
              <h3 className="label">{kpi.label}</h3>
              <Tip label={`${kpi.hint}. Serie de los últimos 14 días.`} side="top">
                <span className="text-ink3/70" tabIndex={0} role="img" aria-label={kpi.hint}>
                  <Icon name="info" size={12} />
                </span>
              </Tip>
            </div>
            <div className="mt-2">
              <Value kpi={kpi} />
            </div>
            <div className="mt-1.5 flex items-baseline gap-1.5">
              <Delta value={kpi.delta} good={good} window="vs. 7 d previos" />
            </div>
            <div className="-mx-1 mt-auto pb-0.5 pt-2.5">
              <Sparkline
                values={kpi.spark}
                height={26}
                tone={kpi.tone === 'accent' ? 'accent' : 'muted'}
                title={`${kpi.label}: serie diaria`}
              />
            </div>
          </article>
        );
      })}
    </div>
  );
};
