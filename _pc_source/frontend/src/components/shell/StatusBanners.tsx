import React from 'react';
import { Icon } from '../ui/Icon';

interface Props {
  loadError: string | null;
  metricsError: string | null;
  actionError: string | null;
  onRetryData: () => void;
  onRetryMetrics: () => void;
  onClearAction: () => void;
}

const Banner: React.FC<{ tone: 'warn' | 'neg'; children: React.ReactNode; action: React.ReactNode }> = ({ tone, children, action }) => (
  <div
    role="alert"
    className={`flex items-start justify-between gap-3 rounded-ctl border px-3 py-2 text-[11.5px] ${
      tone === 'warn' ? 'border-warn/35 bg-warn/[0.06] text-warn' : 'border-neg/35 bg-neg/[0.06] text-neg'
    }`}
  >
    <span className="leading-relaxed">{children}</span>
    <span className="shrink-0">{action}</span>
  </div>
);

/** Fallos visibles y accionables: nunca se oculta un backend caído. */
export const StatusBanners: React.FC<Props> = ({ loadError, metricsError, actionError, onRetryData, onRetryMetrics, onClearAction }) => {
  if (!loadError && !metricsError && !actionError) return null;
  return (
    <div className="space-y-1.5 px-3 pt-2 sm:px-5">
      {loadError && (
        <Banner
          tone="warn"
          action={
            <button type="button" onClick={onRetryData} className="btn btn-sm">
              Reintentar
            </button>
          }
        >
          Datos incompletos: {loadError}
        </Banner>
      )}
      {metricsError && (
        <Banner
          tone="warn"
          action={
            <button type="button" onClick={onRetryMetrics} className="btn btn-sm">
              Reintentar
            </button>
          }
        >
          Métricas no disponibles: {metricsError}
        </Banner>
      )}
      {actionError && (
        <Banner
          tone="neg"
          action={
            <button type="button" onClick={onClearAction} aria-label="Cerrar aviso" className="btn btn-ghost btn-sm px-1">
              <Icon name="close" size={13} />
            </button>
          }
        >
          {actionError}
        </Banner>
      )}
    </div>
  );
};
