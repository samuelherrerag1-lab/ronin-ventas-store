import React from 'react';
import { CheckIcon, CrossIcon } from './publishUi';

type IconProps = { className?: string };
const ICON = 'w-3.5 h-3.5 shrink-0';

export const LockIcon: React.FC<IconProps> = ({ className = ICON }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} aria-hidden="true">
    <rect x="5" y="10" width="14" height="10" rx="2" />
    <path strokeLinecap="round" d="M8 10V7a4 4 0 0 1 8 0v3" />
  </svg>
);

export const PlayIcon: React.FC<IconProps> = ({ className = ICON }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M8 5.5v13l10-6.5-10-6.5Z" />
  </svg>
);

export const AlertIcon: React.FC<IconProps> = ({ className = ICON }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} aria-hidden="true">
    <circle cx="12" cy="12" r="9" />
    <path strokeLinecap="round" d="M12 8v5m0 3h.01" />
  </svg>
);

export function statusTone(loggedIn: boolean, status: string): string {
  if (loggedIn) return 'bg-emerald-950/60 border-emerald-500/40 text-emerald-300';
  if (status === 'blocked' || status === 'error') return 'bg-rose-950/50 border-rose-500/40 text-rose-200';
  return 'bg-zinc-900 border-zinc-700 text-zinc-400';
}

export function shotUrl(jobId: string | undefined, path: string | null | undefined): string | null {
  if (!jobId || !path) return null;
  const name = path.split(/[\\/]/).pop();
  return name ? `/api/social/jobs/${encodeURIComponent(jobId)}/evidence/${encodeURIComponent(name)}` : null;
}

export const JobPieceStatus: React.FC<{ status: string }> = ({ status }) => {
  const ok = status === 'published' || status === 'dry_run_ok';
  const failed = status === 'failed';
  const tone = ok ? 'bg-emerald-950/50 border-emerald-500/40 text-emerald-300'
    : failed ? 'bg-rose-950/50 border-rose-500/40 text-rose-200'
      : 'bg-zinc-900 border-zinc-700 text-zinc-400';
  return (
    <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded border text-[10px] font-mono-tech font-bold uppercase ${tone}`}>
      {ok ? <CheckIcon /> : failed ? <CrossIcon /> : <AlertIcon />}
      {status}
    </span>
  );
};
