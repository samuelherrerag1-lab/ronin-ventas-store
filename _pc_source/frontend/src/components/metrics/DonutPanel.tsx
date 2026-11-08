import React from 'react';
import { Icon } from '../ui/Icon';
import { Panel, PanelHead } from '../ui/primitives';
import { num, pct, usd } from '../../utils/format';
import type { MetricsSummaryResponse } from '../../types/domain';

interface Props {
  summary: MetricsSummaryResponse | null;
}

const R = 46;
const C = 2 * Math.PI * R;

/** Reparto de ingresos por pasarela con anillo fino y cifras a la derecha. */
export const DonutPanel: React.FC<Props> = ({ summary }) => {
  const gumroad = summary?.gumroad_revenue_usd ?? 0;
  const hotmart = summary?.hotmart_revenue_usd ?? 0;
  const total = gumroad + hotmart;
  const share = total > 0 ? gumroad / total : 0;

  return (
    <Panel className="flex flex-col">
      <PanelHead title="Ingresos por pasarela" icon="dollar" />
      <div className="flex flex-1 flex-col gap-3 p-4">
        {total <= 0 ? (
          <div className="flex flex-1 flex-col items-center justify-center gap-2 text-center">
            <Icon name="dollar" size={18} className="text-ink3" />
            <p className="text-[12.5px] text-ink">Sin ingresos en el periodo</p>
            <p className="max-w-[30ch] text-[10.5px] leading-relaxed text-ink3">
              Gumroad (USD) y Hotmart (COP convertido) aparecen al importar ventas.
            </p>
          </div>
        ) : (
          <>
            <div className="flex items-center justify-center">
              <div className="relative h-[132px] w-[132px]">
                <svg viewBox="0 0 120 120" className="h-full w-full -rotate-90" aria-hidden="true">
                  <circle cx="60" cy="60" r={R} fill="none" stroke="var(--panel-3)" strokeWidth="9" />
                  <circle
                    cx="60"
                    cy="60"
                    r={R}
                    fill="none"
                    stroke="#8a857c"
                    strokeWidth="9"
                    strokeDasharray={`${((1 - share) * C).toFixed(2)} ${C.toFixed(2)}`}
                    strokeDashoffset={`${(-share * C).toFixed(2)}`}
                  />
                  <circle
                    cx="60"
                    cy="60"
                    r={R}
                    fill="none"
                    stroke="var(--accent)"
                    strokeWidth="9"
                    strokeLinecap="butt"
                    strokeDasharray={`${(share * C).toFixed(2)} ${C.toFixed(2)}`}
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="num text-[17px] leading-none text-ink">{usd(total, 0)}</span>
                  <span className="mt-1 text-[10px] text-ink3">USD neto</span>
                </div>
              </div>
            </div>
            <ul className="space-y-1.5">
              <li className="flex items-center justify-between gap-2 text-[11.5px]">
                <span className="flex items-center gap-1.5 text-ink2">
                  <span className="dot bg-accent" aria-hidden="true" />
                  Gumroad
                </span>
                <span className="num text-ink">
                  {usd(gumroad, 2)} <span className="ml-1 text-ink3">{pct(share * 100, 0)}</span>
                </span>
              </li>
              <li className="flex items-center justify-between gap-2 text-[11.5px]">
                <span className="flex items-center gap-1.5 text-ink2">
                  <span className="dot bg-[#8a857c]" aria-hidden="true" />
                  Hotmart
                </span>
                <span className="num text-ink">
                  {usd(hotmart, 2)} <span className="ml-1 text-ink3">{pct((1 - share) * 100, 0)}</span>
                </span>
              </li>
            </ul>
          </>
        )}
      </div>
      <footer className="grid grid-cols-3 divide-x divide-line border-t border-line text-center">
        <div className="px-2 py-2">
          <p className="text-[9.5px] text-ink3">AOV</p>
          <p className="num mt-0.5 text-[12px] text-ink">{summary?.aov_usd != null ? usd(summary.aov_usd) : '—'}</p>
        </div>
        <div className="px-2 py-2">
          <p className="text-[9.5px] text-ink3">Ventas</p>
          <p className="num mt-0.5 text-[12px] text-ink">{num(summary?.total_sales ?? 0)}</p>
        </div>
        <div className="px-2 py-2">
          <p className="text-[9.5px] text-ink3">RPM</p>
          <p className="num mt-0.5 text-[12px] text-ink">{summary?.rpm_usd != null ? usd(summary.rpm_usd) : '—'}</p>
        </div>
      </footer>
    </Panel>
  );
};
