/** Panel 03: destinos de publicación. Solo estado real: nada conectado, nada enviado. */

import React from 'react';
import { LockIcon } from './StudioIcons';

const ThreadsMark: React.FC = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6} strokeLinecap="round" className="w-4 h-4" aria-hidden="true">
    <circle cx="12" cy="12" r="8.5" />
    <circle cx="12" cy="12" r="3.6" />
    <path d="M15.6 8.6v3.6a2.4 2.4 0 0 0 4.8 0" />
  </svg>
);

const PinterestMark: React.FC = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4" aria-hidden="true">
    <path d="M9 3.5h6l-1.1 6.2 3.6 3.1v2.2H6.5v-2.2l3.6-3.1L9 3.5Z" />
    <path d="M12 15v6" />
  </svg>
);

const GumroadMark: React.FC = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4" aria-hidden="true">
    <path d="M4.8 8h14.4l-1.4 12H6.2L4.8 8Z" />
    <path d="M9 8V6.2a3 3 0 0 1 6 0V8" />
  </svg>
);

const HotmartMark: React.FC = () => (
  <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4" aria-hidden="true">
    <path d="M12 2C9.5 6 7 9 7 13a5 5 0 0 0 10 0c0-1.5-.5-3-1.5-4.5C14.5 10 13 11.5 13 13a1 1 0 1 1-2 0c0-2.5 2-4.5 3-6-1 0-2.5 1-3.5 2.5C10 8 11 5 12 2Z" />
  </svg>
);

interface PlatformTarget {
  id: string;
  name: string;
  asset: string;
  connected: boolean;
  Icon: React.FC;
}

const PLATFORMS: PlatformTarget[] = [
  { id: 'threads', name: 'Threads', asset: 'Avatar 1:1 + Banner 1500×500', connected: false, Icon: ThreadsMark },
  { id: 'pinterest', name: 'Pinterest', asset: 'Pin 2:3 · 1000×1500', connected: false, Icon: PinterestMark },
  { id: 'gumroad', name: 'Gumroad', asset: 'Avatar 1:1 + Open Graph 1200×630', connected: false, Icon: GumroadMark },
  { id: 'hotmart', name: 'Hotmart', asset: 'Avatar 1:1 + Open Graph 1200×630', connected: false, Icon: HotmartMark },
];

export const PlatformApplyPanel: React.FC = () => {
  const connectedCount = PLATFORMS.filter((platform) => platform.connected).length;

  return (
    <section aria-labelledby="platform-panel-title" className="bg-[#090b10] border border-white/[0.08] rounded-2xl p-4 space-y-3">
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-[10px] font-mono-tech font-bold uppercase tracking-wider text-[#E07A5F]">03 / Distribución</p>
          <h2 id="platform-panel-title" className="text-sm font-bold text-white font-grotesque mt-0.5">Aplicar a plataformas</h2>
          <p className="text-[11px] text-zinc-500 mt-1 leading-snug">Las variantes se generan localmente. Ningún archivo sale de este equipo.</p>
        </div>
        <span className="shrink-0 text-[9px] font-mono-tech px-2 py-1 rounded-lg border border-white/[0.08] bg-black/40 text-zinc-400 tabular-nums">
          {connectedCount} / {PLATFORMS.length} conectados
        </span>
      </div>

      <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
        {PLATFORMS.map(({ id, name, asset, connected, Icon }) => (
          <li key={id} className="rounded-xl border border-white/[0.06] bg-black/40 p-3 flex flex-col gap-2.5">
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-center gap-2 min-w-0">
                <span className="w-8 h-8 shrink-0 rounded-lg bg-white/[0.04] border border-white/10 flex items-center justify-center text-zinc-300">
                  <Icon />
                </span>
                <div className="min-w-0">
                  <p className="text-xs font-bold text-white font-grotesque leading-tight">{name}</p>
                  <p className="text-[10px] text-zinc-500 font-mono-tech mt-0.5 truncate" title={asset}>{asset}</p>
                </div>
              </div>
              <span className={`shrink-0 flex items-center gap-1 text-[9px] font-mono-tech px-1.5 py-0.5 rounded border ${
                connected
                  ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300'
                  : 'border-amber-500/30 bg-amber-500/10 text-amber-300'
              }`}>
                <span className={`w-1.5 h-1.5 rounded-full ${connected ? 'bg-emerald-400' : 'bg-amber-400'}`} aria-hidden="true" />
                {connected ? 'Conectado' : 'Requiere conexión'}
              </span>
            </div>

            <button
              type="button"
              disabled
              aria-describedby="platform-connect-note"
              className="mt-auto inline-flex items-center justify-center gap-1.5 w-full px-2 py-1.5 rounded-lg border border-white/[0.08] bg-white/[0.02] text-[10px] font-mono-tech font-bold text-zinc-500 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              <LockIcon className="w-3 h-3" />
              Aplicar identidad
            </button>
          </li>
        ))}
      </ul>

      <p id="platform-connect-note" className="flex items-start gap-1.5 text-[10px] text-zinc-500 leading-snug pt-1 border-t border-white/[0.06]">
        <LockIcon className="w-3.5 h-3.5 shrink-0 mt-0.5 text-amber-400/80" />
        <span>
          Sin conector verificado no hay publicación. Este módulo nunca simula una subida: habilita cada plataforma desde
          <span className="text-zinc-300"> Customizations &amp; Connectors Hub</span> y la conexión aparecerá reflejada aquí cuando su diagnóstico mida una sesión real.
        </span>
      </p>
    </section>
  );
};
