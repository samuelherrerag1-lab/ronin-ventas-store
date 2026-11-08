import React, { useState } from 'react';
import { copyText } from '../../utils/clipboard';

type IconProps = { className?: string };

const base = 'w-3.5 h-3.5 shrink-0';

export const CheckIcon: React.FC<IconProps> = ({ className = base }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.2} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="m5 12.5 4.5 4.5L19 7" />
  </svg>
);

export const CrossIcon: React.FC<IconProps> = ({ className = base }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.2} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M6 6l12 12M18 6 6 18" />
  </svg>
);

export const RefreshIcon: React.FC<IconProps> = ({ className = base }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M20 11a8 8 0 1 0-2.34 5.66M20 4v7h-7" />
  </svg>
);

export const CopyIcon: React.FC<IconProps> = ({ className = base }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} aria-hidden="true">
    <rect x="9" y="9" width="11" height="11" rx="2" />
    <path strokeLinecap="round" d="M15 5H6a2 2 0 0 0-2 2v9" />
  </svg>
);

export const LinkIcon: React.FC<IconProps> = ({ className = base }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M10 13a5 5 0 0 0 7.07 0l2-2A5 5 0 0 0 12 4l-1 1M14 11a5 5 0 0 0-7.07 0l-2 2A5 5 0 0 0 12 20l1-1" />
  </svg>
);

export const StoreIcon: React.FC<IconProps> = ({ className = base }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.7} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M4 9h16M5 9V6.5A2.5 2.5 0 0 1 7.5 4h9A2.5 2.5 0 0 1 19 6.5V9M5 9v9.5A1.5 1.5 0 0 0 6.5 20h11a1.5 1.5 0 0 0 1.5-1.5V9M9 12h6" />
  </svg>
);

export const WarningIcon: React.FC<IconProps> = ({ className = base }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v4m0 3.5h.01M10.3 4.1 2.8 17.2A1.8 1.8 0 0 0 4.4 20h15.2a1.8 1.8 0 0 0 1.6-2.8L13.7 4.1a1.9 1.9 0 0 0-3.4 0Z" />
  </svg>
);

export const ExternalIcon: React.FC<IconProps> = ({ className = 'w-3 h-3 shrink-0' }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.2} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 19.5l15-15m0 0H8.25m11.25 0v11.25" />
  </svg>
);

export const Section: React.FC<{
  title: string;
  subtitle?: string;
  badge?: React.ReactNode;
  actions?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}> = ({ title, subtitle, badge, actions, children, className = '' }) => (
  <section className={`bg-[#090b10] border border-white/[0.08] rounded-2xl p-4 space-y-3 ${className}`}>
    <div className="flex flex-wrap items-start justify-between gap-2 border-b border-white/[0.06] pb-2.5">
      <div className="min-w-0">
        <h2 className="text-xs font-bold uppercase tracking-wider text-zinc-200 font-mono-tech flex items-center gap-2">
          {title}
          {badge}
        </h2>
        {subtitle && <p className="text-[11px] text-zinc-400 mt-1 leading-relaxed">{subtitle}</p>}
      </div>
      {actions && <div className="flex items-center gap-2 shrink-0">{actions}</div>}
    </div>
    {children}
  </section>
);

export const PendingNotice: React.FC<{ endpoint: string; detail?: string; onRetry?: () => void }> = ({
  endpoint,
  detail,
  onRetry,
}) => (
  <div role="status" className="p-3 rounded-xl bg-amber-500/[0.07] border border-amber-500/30 text-xs text-amber-200 space-y-2">
    <div className="flex items-center gap-2 font-mono-tech font-bold uppercase tracking-wider text-[11px]">
      <WarningIcon className="w-4 h-4" />
      Pendiente en backend
    </div>
    <p className="text-[11px] text-amber-100/80 leading-relaxed">
      El endpoint <code className="font-mono-tech text-amber-200">{endpoint}</code> todavía no responde.
      {detail ? ` Detalle: ${detail}` : ' Se activará en cuanto backend-core lo publique.'}
    </p>
    {onRetry && (
      <button
        type="button"
        onClick={onRetry}
        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-amber-500/15 hover:bg-amber-500/25 border border-amber-500/40 text-amber-200 text-[11px] font-mono-tech font-bold transition"
      >
        <RefreshIcon />
        Reintentar
      </button>
    )}
  </div>
);

export const InlineError: React.FC<{ message: string; onRetry?: () => void }> = ({ message, onRetry }) => (
  <div role="alert" className="p-3 rounded-xl bg-rose-950/40 border border-rose-500/40 text-[11px] text-rose-200 flex flex-wrap items-center justify-between gap-2">
    <span className="leading-relaxed break-words">{message}</span>
    {onRetry && (
      <button
        type="button"
        onClick={onRetry}
        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-rose-500/15 hover:bg-rose-500/25 border border-rose-500/40 text-rose-200 font-mono-tech font-bold transition"
      >
        <RefreshIcon />
        Reintentar
      </button>
    )}
  </div>
);

export const CopyButton: React.FC<{
  text: string;
  label: string;
  className?: string;
}> = ({ text, label, className = '' }) => {
  const [state, setState] = useState<'idle' | 'ok' | 'fail'>('idle');
  const handle = () => {
    void copyText(text).then((ok) => {
      setState(ok ? 'ok' : 'fail');
      window.setTimeout(() => setState('idle'), 1600);
    });
  };
  return (
    <button
      type="button"
      onClick={handle}
      aria-label={`${label}: copiar al portapapeles`}
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-mono-tech font-bold border transition ${
        state === 'fail'
          ? 'bg-rose-950/50 border-rose-500/40 text-rose-200'
          : state === 'ok'
            ? 'bg-emerald-950/50 border-emerald-500/40 text-emerald-200'
            : 'bg-white/[0.04] hover:bg-white/[0.08] border-white/[0.1] text-zinc-200'
      } ${className}`}
    >
      <CopyIcon />
      {state === 'ok' ? 'Copiado' : state === 'fail' ? 'No se pudo copiar' : label}
    </button>
  );
};
