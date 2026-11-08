import React from 'react';
import { STATUS_LABELS, type StatusTone } from './connectorMeta';

export const cx = (...parts: Array<string | false | null | undefined>) =>
  parts.filter(Boolean).join(' ');

type IconProps = { className?: string };

export const Spinner: React.FC<IconProps> = ({ className = 'h-4 w-4' }) => (
  <svg className={cx('animate-spin', className)} viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <circle cx="12" cy="12" r="9" stroke="currentColor" strokeOpacity=".25" strokeWidth="2.5" />
    <path d="M21 12a9 9 0 0 0-9-9" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
  </svg>
);

export const ChevronDown: React.FC<IconProps & { open?: boolean }> = ({ className = 'h-4 w-4', open }) => (
  <svg
    className={cx(className, 'transition-transform duration-200 ease-out', open && 'rotate-180')}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.8"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
  >
    <path d="m6 9 6 6 6-6" />
  </svg>
);

export const BoltIcon: React.FC<IconProps> = ({ className = 'h-4 w-4' }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" aria-hidden="true">
    <path d="M13 2.5 4.8 13.5h6l-1 8 8.4-11h-6l.8-8Z" />
  </svg>
);

export const ConnectIcon: React.FC<IconProps> = ({ className = 'h-4 w-4' }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M9.5 7H6.5A2.5 2.5 0 0 0 4 9.5v8A2.5 2.5 0 0 0 6.5 20h8a2.5 2.5 0 0 0 2.5-2.5v-3" />
    <path d="M14.5 4H20v5.5M20 4l-8.5 8.5" />
  </svg>
);

export const PulseIcon: React.FC<IconProps> = ({ className = 'h-4 w-4' }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M3 12h4l2.5-6.5 4.5 13 2.5-6.5h4.5" />
  </svg>
);

export const TerminalIcon: React.FC<IconProps> = ({ className = 'h-4 w-4' }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <rect x="3" y="5" width="18" height="14" rx="2.5" />
    <path d="m7.5 10 2.8 2.2-2.8 2.3M13 14.5h3.5" />
  </svg>
);

export const SearchIcon: React.FC<IconProps> = ({ className = 'h-4 w-4' }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" aria-hidden="true">
    <circle cx="11" cy="11" r="6.5" />
    <path d="m16 16 4 4" />
  </svg>
);

export const CloseIcon: React.FC<IconProps> = ({ className = 'h-3.5 w-3.5' }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
    <path d="M6 6l12 12M18 6 6 18" />
  </svg>
);

const PILL_TONE: Record<StatusTone, { wrap: string; dot: string }> = {
  ok: {
    wrap: 'border-emerald-400/20 bg-emerald-400/[0.07] text-emerald-300',
    dot: 'bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.7)]',
  },
  fail: { wrap: 'border-rose-400/25 bg-rose-400/[0.07] text-rose-300', dot: 'bg-rose-400' },
  idle: { wrap: 'border-white/[0.07] bg-white/[0.03] text-zinc-400', dot: 'bg-zinc-500' },
};

export const StatusPill: React.FC<{ tone: StatusTone }> = ({ tone }) => (
  <span
    className={cx(
      'inline-flex h-6 shrink-0 items-center gap-1.5 rounded-full border px-2 text-[11px] font-medium leading-none',
      PILL_TONE[tone].wrap,
    )}
  >
    <span className={cx('h-1.5 w-1.5 rounded-full', PILL_TONE[tone].dot)} />
    {STATUS_LABELS[tone]}
  </span>
);

export const GlobalRing: React.FC<{ connected: number; total: number; failing?: number }> = ({
  connected,
  total,
  failing = 0,
}) => {
  const radius = 15;
  const circumference = 2 * Math.PI * radius;
  const ratio = total > 0 ? Math.min(connected / total, 1) : 0;
  const label = `${connected} de ${total} conectados${failing > 0 ? `, ${failing} con falla` : ''}`;

  return (
    <div
      className="relative flex h-11 w-11 shrink-0 items-center justify-center"
      role="img"
      aria-label={label}
      title={label}
    >
      {failing > 0 && (
        <span
          aria-hidden="true"
          className="absolute right-0 top-0 h-2 w-2 rounded-full bg-rose-400 shadow-[0_0_0_2px_#070a12]"
        />
      )}
      <svg className="h-11 w-11 -rotate-90" viewBox="0 0 40 40" aria-hidden="true">
        <circle cx="20" cy="20" r={radius} fill="none" stroke="rgba(255,255,255,0.09)" strokeWidth="3" />
        <circle
          cx="20"
          cy="20"
          r={radius}
          fill="none"
          stroke="#34d399"
          strokeWidth="3"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={circumference * (1 - ratio)}
          className="transition-[stroke-dashoffset] duration-300 ease-out"
        />
      </svg>
      <span aria-hidden="true" className="absolute font-mono-tech text-[11px] font-medium tabular-nums text-zinc-100">
        {connected}
        <span className="text-zinc-400/80">/{total}</span>
      </span>
    </div>
  );
};
