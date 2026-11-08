import React from 'react';
import { Icon } from '../ui/Icon';
import { KpiGrid } from './KpiGrid';
import { FunnelPanel } from './FunnelPanel';
import { KillPanel } from './KillPanel';
import { ActionsPanel, RoutesPanel } from './Panels';
import { useHomeModel } from './useHomeModel';
import type { MetricsState } from '../../hooks/useMetrics';
import type { CustomizationsOverview, PinterestPinItem, ProductSKU, ThreadsPostItem } from '../../types/domain';
import type { NavTabId } from '../shell/nav';

interface Props {
  products: ProductSKU[];
  threads: ThreadsPostItem[];
  pins: PinterestPinItem[];
  customizations: CustomizationsOverview | null;
  metrics: MetricsState;
  onNavigate: (tab: NavTabId) => void;
  onMutateHook: (pieceId: string) => void;
}

/** Pantalla por defecto: la pregunta del día es “¿qué doblo y qué mato hoy?”. */
export const HomeView: React.FC<Props> = ({ products, threads, pins, customizations, metrics, onNavigate, onMutateHook }) => {
  const model = useHomeModel({
    products,
    threads,
    pins,
    customizations,
    summary: metrics.summary,
    raw: metrics.raw,
    demo: metrics.demo,
  });

  const go = (tab: string) => onNavigate(tab as NavTabId);
  const needsImport = !model.hasData && !model.demo;

  return (
    <div className="space-y-3 sm:space-y-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div className="min-w-0">
          <h1 className="font-display text-[26px] leading-none text-ink">Command Center</h1>
          <p className="mt-2 max-w-[68ch] text-[12.5px] leading-relaxed text-ink2">{model.finding}</p>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          {model.demo && (
            <span className="chip border-transparent bg-warn/10 text-warn">
              <Icon name="info" size={11} />
              demo etiquetada
            </span>
          )}
          <button type="button" onClick={() => go('metrics_radar')} className="btn btn-primary">
            <Icon name={needsImport ? 'download' : 'chart'} size={14} />
            {needsImport ? 'Importar CSV' : 'Abrir Radar'}
          </button>
        </div>
      </div>

      <KpiGrid kpis={model.kpis} loading={metrics.loading && !metrics.summary} />
      <p className="text-[10px] text-ink3">
        Acumulado del registro · serie de los últimos 14 días
        {metrics.summary && !model.hasData && !model.demo ? ' · sin datos reales' : ''}
      </p>

      <div className="grid grid-cols-1 gap-3 lg:grid-cols-12 lg:gap-4">
        <div className="lg:col-span-7">
          <FunnelPanel model={model} onOpenMetrics={() => go('metrics_radar')} />
        </div>
        <div className="lg:col-span-5">
          <KillPanel
            model={model}
            onMutateHook={onMutateHook}
            onOpenMetrics={() => go('metrics_radar')}
            onOpenBait={() => go('bait_studio')}
          />
        </div>
        <div className="lg:col-span-5">
          <ActionsPanel model={model} onNavigate={go} />
        </div>
        <div className="lg:col-span-7">
          <RoutesPanel model={model} onNavigate={go} />
        </div>
      </div>
    </div>
  );
};
