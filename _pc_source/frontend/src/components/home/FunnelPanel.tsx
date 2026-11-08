import React from 'react';
import { Icon } from '../ui/Icon';
import { Panel, PanelHead } from '../ui/primitives';
import { Tip } from '../ui/Tooltip';
import { num, pct } from '../../utils/format';
import type { HomeModel } from './useHomeModel';

interface Props {
  model: HomeModel;
  onOpenMetrics: () => void;
}

const TONES = ['bg-[#2a2a33]', 'bg-[#41414e]', 'bg-accent'] as const;
const TEXT = ['text-ink3', 'text-ink3', 'text-accent'] as const;

/** Embudo como escalera de tres peldaños: cada barra mide contra impresiones. */
export const FunnelPanel: React.FC<Props> = ({ model, onOpenMetrics }) => {
  const { funnel } = model;
  const max = Math.max(1, funnel[0]?.value ?? 0);
  const empty = (funnel[0]?.value ?? 0) === 0 && (funnel[2]?.value ?? 0) === 0;

  return (
    <Panel className="flex h-full flex-col">
      <PanelHead
        title="Embudo"
        icon="layers"
        hint="impresiones → clics → ventas"
        actions={
          <button type="button" onClick={onOpenMetrics} className="btn btn-ghost btn-sm">
            Radar
            <Icon name="arrow-right" size={12} />
          </button>
        }
      />
      <div className="flex-1 p-4">
        {empty ? (
          <div className="flex h-full min-h-[180px] flex-col items-center justify-center gap-2 text-center">
            <Icon name="layers" size={18} className="text-ink3" />
            <p className="text-[12.5px] text-ink">El embudo está vacío</p>
            <p className="max-w-[38ch] text-[11px] leading-relaxed text-ink3">
              Se llena con impresiones de piezas y ventas importadas. Sin registros no se dibuja una curva.
            </p>
          </div>
        ) : (
          <div className="space-y-1">
            {funnel.map((stage, index) => {
              const width = 6 + 94 * Math.sqrt(stage.value / max);
              const share = max > 0 ? (stage.value / max) * 100 : 0;
              return (
                <div key={stage.key} className="pb-1.5">
                  <div className="mb-1.5 flex items-baseline justify-between gap-2">
                    <span className="text-[11.5px] text-ink2">{stage.label}</span>
                    <span className="num text-[13px] text-ink">{num(stage.value)}</span>
                  </div>
                  <Tip
                    side="top"
                    label={
                      <span className="block">
                        <b className="block text-[11px] text-ink">{num(stage.value)} {stage.label.toLowerCase()}</b>
                        <span className="text-ink2">
                          {index === 0
                            ? '100% del total'
                            : `${pct(stage.rate)} de ${index === 1 ? 'impresiones' : 'clics'} · ${pct(share)} del embudo`}
                        </span>
                      </span>
                    }
                  >
                    <button
                      type="button"
                      onClick={onOpenMetrics}
                      aria-label={`${stage.label}: ${num(stage.value)}. Abrir Radar de métricas`}
                      className="group block h-[30px] w-full rounded-[3px] bg-[#141419]"
                    >
                      <span
                        className={`flex h-full items-center justify-end rounded-[3px] pr-2 transition-[width] duration-220 ${TONES[index]}`}
                        style={{ width: `${width}%` }}
                      >
                        <span className={`num text-[10px] ${TEXT[index]}`}>{pct(share, 0)}</span>
                      </span>
                    </button>
                  </Tip>
                  {index < funnel.length - 1 && (
                    <p className="mt-1.5 flex items-center gap-1 text-[10.5px] text-ink3">
                      <Icon name="arrow-down-right" size={11} className="text-ink3" />
                      <span className="num text-ink2">{pct(funnel[index + 1].rate)}</span>
                      {index === 0 ? 'pasan a clics' : 'cierran venta'}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
      <footer className="flex items-center justify-between border-t border-line px-4 py-2 text-[10.5px] text-ink3">
        <span>{model.demo ? 'Datos demo etiquetados' : 'Acumulado del periodo'}</span>
        <span className="num">{num(model.totals.saves)} saves</span>
      </footer>
    </Panel>
  );
};
