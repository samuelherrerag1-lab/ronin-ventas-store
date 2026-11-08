import React, { useState } from 'react';
import { Icon } from '../ui/Icon';
import { CountUp } from '../ui/CountUp';
import { Panel, PanelHead } from '../ui/primitives';
import { num, pct, usd } from '../../utils/format';
import type { MetricsSummaryResponse } from '../../types/domain';
import { projectWhatIf, whatIfBase } from './metricsModel';

interface Props {
  summary: MetricsSummaryResponse | null;
  demo: boolean;
}

const KNOBS = [
  { key: 'ctrLift', label: 'CTR', min: -40, max: 80, unit: '%', hint: 'Mejora del gancho' },
  { key: 'closeLift', label: 'Cierre', min: -40, max: 80, unit: '%', hint: 'Clics que compran' },
  { key: 'priceLift', label: 'Precio', min: -30, max: 60, unit: '%', hint: 'Precio medio' },
] as const;

type KnobKey = (typeof KNOBS)[number]['key'];

/** Simulador what-if sobre las cifras reales del periodo, recalculado al mover el slider. */
export const WhatIfPanel: React.FC<Props> = ({ summary, demo }) => {
  const [knobs, setKnobs] = useState<Record<KnobKey, number>>({ ctrLift: 0, closeLift: 0, priceLift: 0 });
  const base = whatIfBase(summary);
  const result = base ? projectWhatIf(base, knobs) : null;
  const current = summary?.total_revenue_usd ?? 0;
  const delta = result ? result.revenue - current : 0;
  const dirty = knobs.ctrLift !== 0 || knobs.closeLift !== 0 || knobs.priceLift !== 0;

  return (
    <Panel className="flex flex-col">
      <PanelHead
        title="Simulador what-if"
        icon="sliders"
        hint={demo ? 'sobre datos demo' : 'sobre datos del periodo'}
        actions={
          dirty ? (
            <button type="button" className="btn btn-ghost btn-sm" onClick={() => setKnobs({ ctrLift: 0, closeLift: 0, priceLift: 0 })}>
              Reset
            </button>
          ) : null
        }
      />
      <div className="flex flex-1 flex-col gap-3 p-4">
        {!base ? (
          <div className="flex flex-1 flex-col items-center justify-center gap-2 py-4 text-center">
            <Icon name="sliders" size={17} className="text-ink3" />
            <p className="text-[12.5px] text-ink">Falta la base de cálculo</p>
            <p className="max-w-[34ch] text-[10.5px] leading-relaxed text-ink3">
              El simulador necesita impresiones, clics y ventas registradas. Sin ellos no proyecta nada.
            </p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
              {KNOBS.map((knob) => (
                <div key={knob.key}>
                  <div className="flex items-baseline justify-between gap-2">
                    <label htmlFor={`knob-${knob.key}`} className="text-[11px] text-ink2">
                      {knob.label}
                    </label>
                    <span className="num text-[11px] text-ink">
                      {knobs[knob.key] > 0 ? '+' : ''}
                      {knobs[knob.key]}
                      {knob.unit}
                    </span>
                  </div>
                  <input
                    id={`knob-${knob.key}`}
                    type="range"
                    className="range mt-1"
                    min={knob.min}
                    max={knob.max}
                    step={1}
                    value={knobs[knob.key]}
                    aria-valuetext={`${knobs[knob.key]} por ciento`}
                    aria-describedby={`knob-hint-${knob.key}`}
                    onChange={(event) => setKnobs((current) => ({ ...current, [knob.key]: Number(event.target.value) }))}
                  />
                  <p id={`knob-hint-${knob.key}`} className="mt-0.5 text-[9.5px] text-ink3">{knob.hint}</p>
                </div>
              ))}
            </div>

            <div className="mt-auto rounded-ctl border border-line bg-[#0e0e11] px-3 py-2.5">
              <div className="flex items-baseline justify-between gap-2">
                <span className="text-[10.5px] text-ink3">Ingresos proyectados</span>
                <span className={`num text-[10.5px] ${delta > 0 ? 'text-pos' : delta < 0 ? 'text-neg' : 'text-ink3'}`}>
                  {delta > 0 ? '+' : delta < 0 ? '−' : '±'}
                  {usd(Math.abs(delta), 0)}
                </span>
              </div>
              <div className="mt-1 flex items-end justify-between gap-2">
                <CountUp value={result?.revenue ?? 0} digits={2} prefix="$" className="num text-[19px] leading-none text-ink" />
                <span className="text-[10px] text-ink3">vs. {usd(current, 0)} actuales</span>
              </div>
              <div className="mt-2 grid grid-cols-2 gap-2 border-t border-line pt-2 text-[10px] text-ink3">
                <span>
                  Clics <b className="num ml-1 font-medium text-ink2">{num(result?.clicks ?? 0)}</b>
                </span>
                <span>
                  Ventas <b className="num ml-1 font-medium text-ink2">{num(result?.sales ?? 0)}</b>
                  <span className="ml-1 text-ink3">({pct(base.closeRate * (1 + knobs.closeLift / 100) * 100)} cierre)</span>
                </span>
              </div>
            </div>
            <p className="text-[9.5px] leading-relaxed text-ink3">
              Simulación aritmética sobre los totales del periodo. No es un pronóstico ni modifica datos.
            </p>
          </>
        )}
      </div>
    </Panel>
  );
};
