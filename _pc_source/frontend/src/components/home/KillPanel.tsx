import React from 'react';
import { Icon } from '../ui/Icon';
import { Panel, PanelHead } from '../ui/primitives';
import { pct, num } from '../../utils/format';
import type { HomeModel } from './useHomeModel';

interface Props {
  model: HomeModel;
  onMutateHook: (pieceId: string) => void;
  onOpenMetrics: () => void;
  onOpenBait: () => void;
}

const LIGHTS = [
  { key: 'doblar', label: 'Doblar', color: 'var(--pos)', hint: 'CTR ≥ 2,0%: sube la cadencia al doble.' },
  { key: 'mutar', label: 'Mutar', color: 'var(--warn)', hint: 'Entre 0,8% y 2,0%: cambia el gancho.' },
  { key: 'matar', label: 'Matar', color: 'var(--neg)', hint: 'CTR < 0,8% tras 48 h: se descarta.' },
] as const;

/**
 * Elemento firma: el criterio de 14 días en una sola regla.
 * Semáforo de veredictos + regla de corte con el marcador del CTR actual.
 */
export const KillPanel: React.FC<Props> = ({ model, onMutateHook, onOpenMetrics, onOpenBait }) => {
  const { counts, ctr, trigger, triggerKind, demo } = model;
  const marker = Math.min(100, Math.max(0, ((ctr ?? 0) / 3) * 100));
  const noPieces = counts.doblar + counts.mutar + counts.matar === 0;

  return (
    <Panel className="flex h-full flex-col">
      <PanelHead
        title="Doblar o Matar"
        icon="target"
        hint="ventana de 14 días"
        actions={<span className="chip num border-transparent bg-panel3 px-1.5">CTR {pct(ctr)}</span>}
      />
      <div className="flex flex-1 flex-col gap-3 p-4">
        <div className="grid grid-cols-3 gap-1.5">
          {LIGHTS.map((light) => {
            const value = counts[light.key];
            const on = value > 0;
            return (
              <div
                key={light.key}
                className={`rounded-ctl border bg-panel2/50 px-2 py-1.5 ${on ? 'border-line2' : 'border-line'}`}
                title={light.hint}
              >
                <div className="flex items-center gap-1.5">
                  <span className="dot" style={{ background: on ? light.color : 'var(--line-2)' }} aria-hidden="true" />
                  <span className="text-[10.5px] text-ink3">{light.label}</span>
                </div>
                <p className={`num mt-1 text-[16px] leading-none ${on ? 'text-ink' : 'text-ink3'}`}>{value}</p>
              </div>
            );
          })}
        </div>

        <div>
          <div className="mb-2 flex items-baseline justify-between">
            <span className="text-[10.5px] text-ink3">Regla de corte</span>
            <span className="text-[9.5px] text-ink3">{ctr === null ? 'sin CTR medido' : 'marcador = CTR actual'}</span>
          </div>
          <div className="relative h-[22px]" aria-hidden="true">
            <div className="absolute inset-x-0 top-[10px] flex h-[3px] overflow-hidden rounded-full">
              <span className="bg-neg/50" style={{ width: '26.7%' }} />
              <span className="bg-line2" style={{ width: '40%' }} />
              <span className="flex-1 bg-pos/50" />
            </div>
            <span
              className="absolute top-[2px] h-[19px] w-[2px] rounded-full bg-ink transition-[left] duration-220"
              style={{ left: `calc(${marker}% - 1px)` }}
            />
          </div>
          <div className="relative mt-1 h-3 text-[9px] text-ink3">
            <span className="absolute left-0">0%</span>
            <span className="absolute -translate-x-1/2 text-neg/90" style={{ left: '26.7%' }}>0,8%</span>
            <span className="absolute -translate-x-1/2 text-pos/90" style={{ left: '66.7%' }}>2,0%</span>
            <span className="absolute right-0">3%</span>
          </div>
        </div>

        <div className="mt-auto">
          {noPieces ? (
            <div className="rounded-ctl border border-dashed border-line px-3 py-3">
              <p className="text-[11.5px] text-ink">Sin piezas medidas todavía</p>
              <p className="mt-1 text-[10.5px] leading-relaxed text-ink3">
                El veredicto necesita impresiones y clics por pieza. Con cero registros no hay semáforo.
              </p>
              <button type="button" onClick={onOpenMetrics} className="btn btn-sm mt-2">
                <Icon name="download" size={12} />
                Importar o registrar
              </button>
            </div>
          ) : trigger ? (
            <div className="rounded-ctl border border-line bg-[#0e0e11] px-3 py-2.5">
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <div className="flex items-center gap-1.5">
                    <span className="mono-id truncate text-ink2">{trigger.piece_id}</span>
                    <span className="chip border-transparent bg-panel3 px-1.5 text-[9.5px]">{trigger.platform}</span>
                  </div>
                  <p className="mt-1 truncate text-[10.5px] text-ink3">
                    {trigger.route ?? trigger.reason}
                  </p>
                </div>
                <span className={`num shrink-0 text-[12.5px] ${triggerKind === 'kill' ? 'text-neg' : 'text-pos'}`}>
                  {pct(trigger.ctr, 2)}
                </span>
              </div>
              <button
                type="button"
                onClick={() => (triggerKind === 'kill' ? onMutateHook(trigger.piece_id) : onOpenBait())}
                className="btn btn-sm mt-2 w-full justify-center"
              >
                <Icon name={triggerKind === 'kill' ? 'wrench' : 'bolt'} size={12} className="text-accent" />
                {triggerKind === 'kill' ? 'Mutar gancho verbal' : 'Producir variante ganadora'}
              </button>
            </div>
          ) : null}
        </div>
      </div>
      <footer className="flex items-center justify-between border-t border-line px-4 py-2 text-[10.5px] text-ink3">
        <span className="num">{num(model.totals.clicks)} clics medidos</span>
        <span>{demo ? 'demo' : 'datos reales'}</span>
      </footer>
    </Panel>
  );
};
