import React, { useState } from 'react';
import type { SocialPlatform } from './autoPublishApi';
import { useAutoPublish } from './useAutoPublish';
import { AlertIcon, JobPieceStatus, LockIcon, PlayIcon, shotUrl, statusTone } from './autoPublishUi';
import {
  CheckIcon,
  ExternalIcon,
  InlineError,
  PendingNotice,
  RefreshIcon,
  Section,
  WarningIcon,
} from './publishUi';

const PLATFORMS: Array<{ id: SocialPlatform; label: string }> = [
  { id: 'threads', label: 'Threads' },
  { id: 'pinterest', label: 'Pinterest' },
];

export const AutoPublishPanel: React.FC = () => {
  const [platform, setPlatform] = useState<SocialPlatform>('threads');
  const [dryRun, setDryRun] = useState(true);
  const [armed, setArmed] = useState(false);
  const state = useAutoPublish(platform);
  const job = state.job;
  const running = Boolean(job && !['completed', 'partial', 'failed'].includes(job.status));
  const progress = job?.progress && job.progress.total > 0
    ? Math.round((job.progress.done / job.progress.total) * 100)
    : 0;
  const profile = state.status?.profile;
  const loginBusy = state.busy?.startsWith('login');
  const verifyBusy = state.busy?.startsWith('verify');

  return (
    <Section
      title="Publicador automatico"
      subtitle="Chrome persistente con la UI real. Sin login medido no se publica: el job falla y pide login. Modo seco por defecto."
      badge={
        <span className="px-2 py-0.5 rounded bg-[#E07A5F]/15 border border-[#E07A5F]/30 text-[10px] font-mono-tech text-[#E07A5F] font-bold">
          REAL
        </span>
      }
      actions={
        <button type="button" onClick={state.loadAll} className="inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.1] text-[10px] font-mono-tech font-bold text-zinc-200">
          <RefreshIcon /> Reconsultar
        </button>
      }
    >
      {state.statusPending && <PendingNotice endpoint="/api/social/status" detail={state.statusError ?? undefined} onRetry={state.loadAll} />}
      {!state.statusPending && state.statusError && <InlineError message={state.statusError} onRetry={state.loadAll} />}

      {profile && (
        <div className="flex flex-wrap items-center gap-2 text-[10px] font-mono-tech text-zinc-400">
          <span className="px-1.5 py-0.5 rounded bg-white/[0.05] border border-white/[0.1] truncate max-w-[260px]" title={profile.path}>
            perfil {profile.is_vault ? 'chrome_vault' : 'temporal'} · channel {profile.channel}
          </span>
          {profile.in_use_by && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-amber-950/40 border border-amber-500/40 text-amber-200">
              <LockIcon /> en uso por {profile.in_use_by}
            </span>
          )}
          {profile.browser_busy && <span className="text-amber-200">Chrome ocupado ahora mismo</span>}
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {PLATFORMS.map((item) => {
          const session = state.status?.sessions?.[item.id];
          const loggedIn = Boolean(session?.logged_in);
          return (
            <div key={item.id} className="bg-black/30 border border-white/[0.07] rounded-xl p-2.5 space-y-2">
              <div className="flex items-center justify-between gap-2">
                <span className="text-[11px] font-bold text-zinc-100">{item.label}</span>
                <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded border text-[10px] font-mono-tech font-bold uppercase ${statusTone(loggedIn, session?.status ?? 'unknown')}`}>
                  {loggedIn ? <CheckIcon /> : <LockIcon />}
                  {loggedIn ? 'conectado' : session?.status === 'unknown' || !session ? 'sin verificar' : session.status}
                </span>
              </div>
              <p className="text-[10px] text-zinc-400 leading-relaxed line-clamp-2" title={session?.evidence ?? ''}>
                {session?.account_label ? `@${session.account_label} · ` : ''}
                {session?.evidence ?? 'Sin medicion todavia.'}
              </p>
              <div className="flex items-center gap-1.5 flex-wrap">
                <button
                  type="button"
                  disabled={Boolean(loginBusy)}
                  onClick={() => void state.openLogin(item.id)}
                  className="inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-[#E07A5F]/15 hover:bg-[#E07A5F]/25 border border-[#E07A5F]/40 text-[10px] font-mono-tech font-bold text-[#E07A5F] disabled:opacity-40"
                >
                  <ExternalIcon /> Abrir login
                </button>
                <button
                  type="button"
                  disabled={Boolean(verifyBusy)}
                  onClick={() => void state.verify(item.id)}
                  className="inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.1] text-[10px] font-mono-tech font-bold text-zinc-200 disabled:opacity-40"
                >
                  <RefreshIcon /> Verificar
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {state.notice && (
        <div role="status" className="p-2.5 rounded-xl bg-cyan-500/[0.06] border border-cyan-500/25 text-[10px] text-cyan-100 leading-relaxed break-words">
          {state.notice}
        </div>
      )}

      <div className="space-y-2">
        <div className="flex items-center justify-between gap-2 flex-wrap">
          <div className="flex rounded-lg border border-white/[0.08] bg-black/40 p-0.5" role="tablist" aria-label="Plataforma del publicador">
            {PLATFORMS.map((item) => (
              <button key={item.id} type="button" role="tab" aria-selected={platform === item.id} onClick={() => { setPlatform(item.id); setArmed(false); }}
                className={`px-2.5 py-1 rounded-md text-[10px] font-mono-tech font-bold ${platform === item.id ? 'bg-white/[0.1] text-white' : 'text-zinc-400 hover:text-zinc-200'}`}>
                {item.label}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-1.5 text-[10px] font-mono-tech">
            <button type="button" onClick={state.selectAll} className="px-2 py-1 rounded-lg bg-white/[0.04] border border-white/[0.1] text-zinc-300">Todo</button>
            <button type="button" onClick={state.clear} className="px-2 py-1 rounded-lg bg-white/[0.04] border border-white/[0.1] text-zinc-300">Nada</button>
            <span className="text-zinc-500">{state.selected.length} seleccionadas</span>
          </div>
        </div>

        {state.queuePending && <PendingNotice endpoint="/api/social/queue" detail={state.queueError ?? undefined} onRetry={state.loadAll} />}
        {!state.queuePending && state.queueError && <InlineError message={state.queueError} onRetry={state.loadAll} />}
        <div className="max-h-56 overflow-y-auto space-y-1 pr-1">
          {state.queue.slice(0, 20).map((item) => (
            <label key={item.id} className="flex items-start gap-2 p-2 rounded-lg bg-black/30 border border-white/[0.06] hover:border-white/[0.12] cursor-pointer">
              <input type="checkbox" checked={state.selected.includes(item.id)} onChange={() => state.toggle(item.id)} className="mt-0.5 accent-[#E07A5F]" />
              <span className="min-w-0 flex-1">
                <span className="flex items-center gap-1.5 text-[10px] font-mono-tech text-zinc-400">
                  <span className="text-zinc-300">{item.id}</span>
                  <span>SKU {item.sku_id}</span>
                  {!item.has_image && <span className="text-amber-300">sin imagen</span>}
                  {item.published_url && <a href={item.published_url} target="_blank" rel="noreferrer" className="text-emerald-300 inline-flex items-center gap-1">publicado <ExternalIcon /></a>}
                </span>
                <span className="block text-[10px] text-zinc-300 leading-snug line-clamp-2">{item.text}</span>
              </span>
            </label>
          ))}
          {!state.queuePending && !state.queueError && state.queue.length === 0 && (
            <p className="text-[10px] text-zinc-500 text-center py-3">No hay piezas en cola para esta plataforma.</p>
          )}
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2 border-t border-white/[0.06] pt-2">
        <div className="flex rounded-lg border border-white/[0.08] bg-black/40 p-0.5" role="radiogroup" aria-label="Modo de publicacion">
          <button type="button" role="radio" aria-checked={dryRun} onClick={() => { setDryRun(true); setArmed(false); }}
            className={`px-2.5 py-1 rounded-md text-[10px] font-mono-tech font-bold ${dryRun ? 'bg-white/[0.1] text-white' : 'text-zinc-400'}`}>Probar en seco</button>
          <button type="button" role="radio" aria-checked={!dryRun} onClick={() => { setDryRun(false); setArmed(false); }}
            className={`px-2.5 py-1 rounded-md text-[10px] font-mono-tech font-bold ${!dryRun ? 'bg-rose-500/20 text-rose-200' : 'text-zinc-400'}`}>Publicar ahora</button>
        </div>
        <button
          type="button"
          disabled={Boolean(state.busy) || running || state.selected.length === 0}
          onClick={() => {
            if (dryRun) { void state.publish(true); return; }
            if (!armed) { setArmed(true); return; }
            setArmed(false);
            void state.publish(false);
          }}
          className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-[11px] font-mono-tech font-bold disabled:opacity-40 disabled:cursor-not-allowed ${
            dryRun ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-200 hover:bg-emerald-500/25'
              : armed ? 'bg-rose-500/25 border-rose-400 text-rose-100' : 'bg-rose-500/15 border-rose-500/40 text-rose-200 hover:bg-rose-500/25'
          }`}
        >
          {dryRun ? <PlayIcon /> : <WarningIcon />}
          {running ? 'Trabajando...' : dryRun ? 'Probar en seco' : armed ? 'Confirmar publicacion real' : 'Publicar ahora'}
        </button>
        {!dryRun && <span className="inline-flex items-center gap-1 text-[10px] text-rose-200"><AlertIcon /> Pulsa dos veces para publicar de verdad</span>}
      </div>

      {job && (
        <div className="space-y-2 border-t border-white/[0.06] pt-2">
          <div className="flex items-center justify-between gap-2 text-[10px] font-mono-tech text-zinc-300">
            <span>{job.job_id} · {job.platform} · {job.dry_run ? 'modo seco' : 'PUBLICACION REAL'}</span>
            <span className="uppercase font-bold text-zinc-200">{job.status}</span>
          </div>
          <div className="h-1.5 bg-white/[0.06] rounded-full overflow-hidden" role="progressbar" aria-valuenow={progress} aria-valuemin={0} aria-valuemax={100}>
            <div className="h-full bg-[#E07A5F] transition-all duration-200" style={{ width: `${progress}%` }} />
          </div>
          {job.error && <p className="text-[10px] text-rose-200 leading-relaxed break-words">{job.error}</p>}
          <div className="space-y-1">
            {job.pieces.map((piece) => (
              <div key={piece.id} className="flex items-start justify-between gap-2 p-1.5 rounded-lg bg-black/30 border border-white/[0.05]">
                <div className="min-w-0 space-y-0.5">
                  <div className="flex items-center gap-1.5 text-[10px] font-mono-tech text-zinc-300"><span>{piece.id}</span><JobPieceStatus status={piece.status} /></div>
                  {piece.error && <p className="text-[10px] text-rose-200 break-words">{piece.error}</p>}
                  {piece.post_url && <a href={piece.post_url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-[10px] text-cyan-300 break-all">{piece.post_url} <ExternalIcon /></a>}
                </div>
                {shotUrl(job.job_id, piece.screenshot) && (
                  <a href={shotUrl(job.job_id, piece.screenshot) ?? '#'} target="_blank" rel="noreferrer" className="text-[10px] text-zinc-400 hover:text-zinc-200 shrink-0">evidencia</a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="flex flex-wrap items-center justify-between gap-2 border-t border-white/[0.06] pt-2 text-[10px] font-mono-tech text-zinc-400">
        <span>
          Programacion: {state.schedule?.threads_per_day ?? 5} Threads + {state.schedule?.pinterest_per_day ?? 5} pines/dia
          {state.schedule?.next_slot ? ` · proxima ${state.schedule.next_slot}` : ''}
          {' · '}{state.schedule?.dry_run === false ? 'REAL' : 'seco'}
        </span>
        <button type="button" disabled={state.scheduleSaving} onClick={() => void state.updateSchedule({ enabled: !state.schedule?.enabled })}
          className={`px-2 py-1 rounded-lg border font-bold ${state.schedule?.enabled ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-200' : 'bg-white/[0.04] border-white/[0.1] text-zinc-300'}`}>
          {state.schedule?.enabled ? 'Programacion activa' : 'Activar programacion'}
        </button>
      </div>
      {state.scheduleError && <p className="text-[10px] text-rose-200">{state.scheduleError}</p>}
    </Section>
  );
};
