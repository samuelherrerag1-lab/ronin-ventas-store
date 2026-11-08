import React from 'react';
import type { PublishReadiness } from '../../types/domain';
import { CheckIcon, CrossIcon, InlineError, PendingNotice, Section } from './publishUi';

interface Props {
  data: PublishReadiness | null;
  loading: boolean;
  error: string | null;
  pending: boolean;
  onRetry: () => void;
  checkoutMissing: number;
}

const COUNT_LABELS: Array<{ key: keyof PublishReadiness['counts']; label: string }> = [
  { key: 'skus', label: 'SKUs' },
  { key: 'paid', label: 'De pago' },
  { key: 'leads', label: 'Lead magnets' },
  { key: 'checkouts', label: 'Con checkout' },
  { key: 'deliverables', label: 'Entregables' },
  { key: 'art_covers', label: 'Portadas' },
  { key: 'threads', label: 'Posts Threads' },
  { key: 'pins', label: 'Pines' },
];

export const PublishReadinessPanel: React.FC<Props> = ({
  data,
  loading,
  error,
  pending,
  onRetry,
  checkoutMissing,
}) => {
  const blocked = data ? !data.ready : false;
  return (
    <Section
      title="Checklist de preparación"
      subtitle="Datos reales de /api/publish/readiness. Nada se marca listo sin evidencia."
      badge={
        <span
          className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full border text-[10px] font-mono-tech font-bold uppercase tracking-wider ${
            blocked
              ? 'bg-rose-950/50 border-rose-500/40 text-rose-300'
              : 'bg-emerald-950/50 border-emerald-500/40 text-emerald-300'
          }`}
        >
          <span className={`w-1.5 h-1.5 rounded-full ${blocked ? 'bg-rose-400' : 'bg-emerald-400'}`} />
          {data ? (blocked ? 'Bloqueado' : 'Listo') : 'Sin verificar'}
        </span>
      }
      actions={
        <button
          type="button"
          onClick={onRetry}
          disabled={loading}
          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.1] text-[11px] font-mono-tech text-zinc-200 transition disabled:opacity-50"
        >
          <svg className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" d="M20 11a8 8 0 1 0-2.34 5.66M20 4v7h-7" />
          </svg>
          {loading ? 'Consultando' : 'Reconsultar'}
        </button>
      }
    >
      {pending && <PendingNotice endpoint="/api/publish/readiness" onRetry={onRetry} />}
      {!pending && error && <InlineError message={error} onRetry={onRetry} />}
      {!pending && !error && !data && loading && (
        <div className="text-[11px] text-zinc-500 font-mono-tech animate-pulse py-4">Consultando readiness real...</div>
      )}
      {data && (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {COUNT_LABELS.map(({ key, label }) => (
              <div key={key} className="bg-black/40 border border-white/[0.06] rounded-xl px-2.5 py-2">
                <div className="text-[9px] uppercase tracking-wider text-zinc-500 font-mono-tech">{label}</div>
                <div className="text-lg font-black text-white font-display tabular-nums leading-tight">
                  {data.counts?.[key] ?? 0}
                </div>
              </div>
            ))}
          </div>

          {checkoutMissing > 0 && (
            <div className="p-2.5 rounded-xl bg-amber-500/[0.07] border border-amber-500/30 text-[11px] text-amber-200">
              <b className="font-mono-tech">{checkoutMissing}</b> SKUs de pago siguen sin checkout (Gumroad/Hotmart).
              Configúralos abajo para desbloquear la venta.
            </div>
          )}

          <ul className="space-y-1.5">
            {data.checks.map((check) => (
              <li key={check.id} className="flex items-start gap-2 text-[11px] leading-relaxed">
                <span
                  className={`mt-0.5 w-4 h-4 rounded-full flex items-center justify-center shrink-0 ${
                    check.ok ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'
                  }`}
                >
                  {check.ok ? <CheckIcon className="w-2.5 h-2.5" /> : <CrossIcon className="w-2.5 h-2.5" />}
                </span>
                <span className="min-w-0">
                  <b className={check.ok ? 'text-zinc-200' : 'text-rose-200'}>{check.label}</b>
                  {check.detail && <span className="text-zinc-400"> — {check.detail}</span>}
                </span>
              </li>
            ))}
          </ul>

          {data.blockers.length > 0 && (
            <div className="space-y-1">
              <div className="text-[10px] uppercase tracking-wider text-rose-300 font-mono-tech font-bold">
                Bloqueos ({data.blockers.length})
              </div>
              <div className="flex flex-wrap gap-1.5">
                {data.blockers.map((id) => (
                  <span key={id} className="px-2 py-0.5 rounded bg-rose-950/50 border border-rose-500/30 text-rose-200 font-mono-tech text-[10px]">
                    {id}
                  </span>
                ))}
              </div>
            </div>
          )}

          {data.next_actions.length > 0 && (
            <div className="space-y-1">
              <div className="text-[10px] uppercase tracking-wider text-emerald-300 font-mono-tech font-bold">
                Próximas acciones
              </div>
              <ol className="list-decimal list-inside space-y-0.5 text-[11px] text-zinc-300">
                {data.next_actions.map((action, index) => (
                  <li key={`${index}-${action}`} className="leading-relaxed">{action}</li>
                ))}
              </ol>
            </div>
          )}
        </>
      )}
    </Section>
  );
};
