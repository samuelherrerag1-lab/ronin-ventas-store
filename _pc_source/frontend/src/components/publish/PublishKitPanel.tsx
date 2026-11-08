import React from 'react';
import type { PublishKitItem, PublishPlatform } from '../../types/domain';
import { CopyButton, ExternalIcon, InlineError, LinkIcon, PendingNotice, Section } from './publishUi';

interface Props {
  platform: PublishPlatform;
  onChangePlatform: (platform: PublishPlatform) => void;
  items: PublishKitItem[] | null;
  loading: boolean;
  error: string | null;
  pending: boolean;
  markNote: string | null;
  markingId: string | null;
  onRetry: () => void;
  onMark: (item: PublishKitItem) => void;
}

function absolutePath(route: string): string {
  if (!route) return '';
  if (/^https?:\/\//i.test(route)) return route;
  if (typeof window === 'undefined') return route;
  return `${window.location.origin}${route.startsWith('/') ? '' : '/'}${route}`;
}

const PLATFORM_TABS: Array<{ id: PublishPlatform; label: string }> = [
  { id: 'threads', label: 'Threads' },
  { id: 'pinterest', label: 'Pinterest' },
];

export const PublishKitPanel: React.FC<Props> = ({
  platform,
  onChangePlatform,
  items,
  loading,
  error,
  pending,
  markNote,
  markingId,
  onRetry,
  onMark,
}) => (
  <Section
    title="Cola de contenido"
    subtitle="Texto e imagen listos para copiar. El seguimiento es local: marcar publicado NO publica en la red social."
    badge={
      <span className="px-2 py-0.5 rounded bg-white/[0.05] border border-white/[0.1] text-[10px] font-mono-tech text-zinc-400">
        {items ? `${items.length} piezas` : 'sin datos'}
      </span>
    }
    actions={
      <div className="flex rounded-lg border border-white/[0.08] bg-black/40 p-0.5" role="tablist" aria-label="Plataforma de contenido">
        {PLATFORM_TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            role="tab"
            aria-selected={platform === tab.id}
            onClick={() => onChangePlatform(tab.id)}
            className={`px-2.5 py-1 rounded-md text-[11px] font-mono-tech font-bold transition ${
              platform === tab.id ? 'bg-white/[0.1] text-white' : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>
    }
  >
    <div role="tabpanel" aria-label={`Cola de ${platform}`} className="space-y-2.5">
      {pending && <PendingNotice endpoint={`/api/publish/kit?platform=${platform}`} onRetry={onRetry} />}
      {!pending && error && <InlineError message={error} onRetry={onRetry} />}
      {!pending && !error && loading && (
        <div className="text-[11px] text-zinc-500 font-mono-tech animate-pulse py-3">Cargando cola real...</div>
      )}
      {!pending && !error && !loading && items && items.length === 0 && (
        <div className="p-4 rounded-xl bg-black/40 border border-white/[0.06] text-center text-[11px] text-zinc-500 font-mono-tech">
          No hay piezas en cola para esta plataforma.
        </div>
      )}

      {markNote && (
        <div className="p-2.5 rounded-xl bg-emerald-500/[0.07] border border-emerald-500/30 text-[11px] text-emerald-200 leading-relaxed">
          {markNote}
        </div>
      )}

      {!pending && !error && items && items.map((item) => {
        const link = absolutePath(item.target_route);
        const published = item.status === 'published';
        return (
          <article key={item.id} className="bg-black/30 border border-white/[0.07] rounded-xl p-2.5 space-y-2">
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-center gap-2 min-w-0 text-[10px] font-mono-tech">
                <span className="px-1.5 py-0.5 rounded bg-white/[0.06] border border-white/[0.1] text-zinc-300 truncate max-w-[130px]">{item.id}</span>
                <span className="text-zinc-500 truncate">SKU {item.target_sku_id}</span>
                <span
                  className={`px-1.5 py-0.5 rounded border font-bold uppercase tracking-wider shrink-0 ${
                    published
                      ? 'bg-emerald-950/60 border-emerald-500/40 text-emerald-300'
                      : 'bg-zinc-900 border-zinc-700 text-zinc-400'
                  }`}
                >
                  {published ? 'Publicado (local)' : 'En cola'}
                </span>
              </div>
              {item.image_url && (
                <img
                  src={item.image_url}
                  alt=""
                  loading="lazy"
                  className="w-10 h-10 rounded-lg object-cover border border-white/10 bg-zinc-900 shrink-0"
                  onError={(e) => { e.currentTarget.style.visibility = 'hidden'; }}
                />
              )}
            </div>

            <p className="text-[11px] text-zinc-200 leading-relaxed whitespace-pre-line max-h-40 overflow-y-auto pr-1">
              {item.text}
            </p>

            <div className="flex items-center justify-between gap-2 flex-wrap">
              <a
                href={link}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-[10px] font-mono-tech text-cyan-300 hover:text-cyan-200 truncate max-w-[55%]"
                title={link}
              >
                <LinkIcon className="w-3 h-3" />
                <span className="truncate">{item.target_route}</span>
                <ExternalIcon />
              </a>
              <div className="flex items-center gap-1.5 flex-wrap">
                <CopyButton text={item.text} label="Copiar texto" />
                {link && <CopyButton text={link} label="Copiar link" />}
                <button
                  type="button"
                  onClick={() => onMark(item)}
                  disabled={markingId === item.id || published}
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-mono-tech font-bold border bg-emerald-500/15 border-emerald-500/40 text-emerald-200 hover:bg-emerald-500/25 disabled:opacity-40 disabled:cursor-not-allowed transition"
                >
                  {markingId === item.id ? 'Guardando...' : 'Marcar publicado'}
                </button>
              </div>
            </div>
          </article>
        );
      })}

      <p className="text-[10px] text-zinc-500 leading-relaxed pt-1 border-t border-white/[0.06]">
        Al marcar se guarda solo el estado de seguimiento en este equipo. La publicación en Threads/Pinterest
        sigue siendo manual desde la app oficial.
      </p>
    </div>
  </Section>
);
