import React from 'react';
import { Icon } from '../ui/Icon';
import { Panel, PanelHead } from '../ui/primitives';
import { Tip } from '../ui/Tooltip';
import { num, pct, ratio } from '../../utils/format';
import type { HomeModel } from './useHomeModel';

interface ActionsProps {
  model: HomeModel;
  onNavigate: (tab: string) => void;
}

/** Lo que se hace desde aquí: una fila por trabajo pendiente, con su control. */
export const ActionsPanel: React.FC<ActionsProps> = ({ model, onNavigate }) => (
  <Panel className="flex h-full flex-col">
    <PanelHead
      title="Próximas acciones"
      icon="bolt"
      actions={<span className="chip border-transparent bg-panel3 px-1.5">{model.actions.length}</span>}
    />
    <ul className="flex-1 divide-y divide-line">
      {model.actions.map((action) => (
        <li key={action.id}>
          <button
            type="button"
            onClick={() => onNavigate(action.tab)}
            className="group flex w-full items-center gap-3 px-4 py-2.5 text-left transition-colors duration-150 hover:bg-panel2/70"
          >
            <span className={`shrink-0 ${action.tone === 'accent' ? 'text-accent' : action.tone === 'warn' ? 'text-warn' : 'text-ink3'}`}>
              <Icon name={action.icon} size={16} />
            </span>
            <span className="min-w-0 flex-1">
              <span className="block truncate text-[12.5px] text-ink">{action.title}</span>
              <span className="block truncate text-[10.5px] text-ink3">{action.hint}</span>
            </span>
            <Icon name="chevron-right" size={14} className="shrink-0 text-ink3 transition-colors group-hover:text-ink2" />
          </button>
        </li>
      ))}
    </ul>
  </Panel>
);

interface RoutesProps {
  model: HomeModel;
  onNavigate: (tab: string) => void;
}

/** Rutas puente ordenadas por clics reales; la barra mide contra la mejor ruta. */
export const RoutesPanel: React.FC<RoutesProps> = ({ model, onNavigate }) => {
  const max = Math.max(1, ...model.routes.map((route) => route.clicks));
  return (
    <Panel className="flex h-full flex-col">
      <PanelHead
        title="Rutas con tracción"
        icon="route"
        hint={`${model.routes.length} medidas`}
        actions={
          <button type="button" onClick={() => onNavigate('catalog_factory')} className="btn btn-ghost btn-sm">
            Catálogo
            <Icon name="arrow-right" size={12} />
          </button>
        }
      />
      <div className="flex-1 p-2">
        {model.routes.length === 0 ? (
          <div className="flex min-h-[150px] flex-col items-center justify-center gap-1.5 px-4 text-center">
            <Icon name="route" size={17} className="text-ink3" />
            <p className="text-[12px] text-ink">Sin clics por ruta</p>
            <p className="max-w-[36ch] text-[10.5px] leading-relaxed text-ink3">
              Las rutas se miden cuando una pieza con enlace recibe clics. Aún no hay datos.
            </p>
          </div>
        ) : (
          <ul>
            {model.routes.map((route) => (
              <li key={route.route}>
                <Tip
                  side="top"
                  label={
                    <span className="block">
                      <b className="block text-ink">{route.route}</b>
                      <span className="text-ink2">
                        {num(route.impressions)} impresiones · {num(route.saves)} saves · {pct(route.ctr, 2)} CTR
                      </span>
                    </span>
                  }
                >
                  <button
                    type="button"
                    onClick={() => onNavigate('catalog_factory')}
                    className="grid w-full grid-cols-[1fr_auto] items-center gap-x-3 gap-y-1 rounded-ctl px-2 py-2 text-left transition-colors duration-150 hover:bg-panel2/70"
                  >
                    <span className="mono-id truncate text-ink2">{route.route.replace(/^\//, '')}</span>
                    <span className="num text-[11.5px] text-ink">{num(route.clicks)}</span>
                    <span className="col-span-2 flex items-center gap-2">
                      <span className="h-[3px] flex-1 overflow-hidden rounded-full bg-[#141419]">
                        <span
                          className="block h-full rounded-full bg-accent/70"
                          style={{ width: `${Math.max(3, ratio(route.clicks, max) * 100)}%` }}
                        />
                      </span>
                      <span className="num w-11 text-right text-[10px] text-ink3">{pct(route.ctr, 2)}</span>
                    </span>
                  </button>
                </Tip>
              </li>
            ))}
          </ul>
        )}
      </div>
    </Panel>
  );
};
