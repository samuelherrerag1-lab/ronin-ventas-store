import React from 'react';

export type CoreStatus = 'CONECTADO' | 'FALLA' | 'SIN_VERIFICAR';

interface Props {
  lanUrl: string;
  coreStatus: CoreStatus;
  vertexProjectId?: string | null;
  vertexModel?: string | null;
  loading: boolean;
  onRefresh: () => void;
  onOpenLan: () => void;
}

export const TopHudHeader: React.FC<Props> = ({
  lanUrl,
  coreStatus,
  vertexProjectId,
  vertexModel,
  loading,
  onRefresh,
  onOpenLan,
}) => (
  <header className="min-h-[50px] py-2 border-b border-white/[0.08] px-3 sm:px-5 flex items-center justify-between gap-2 bg-[#08090d]/90 backdrop-blur-xl sticky top-0 z-30 select-none">
    <div className="flex items-center gap-1.5 sm:gap-2 overflow-x-auto no-scrollbar">
      <div className="flex lg:hidden items-center gap-1.5 pr-1 shrink-0">
        <img src="/generated_images/ron_avatar_profile.png" alt="Ron" className="w-6 h-6 rounded-full object-cover ring-1 ring-[#E07A5F]" />
        <span className="font-display text-[11px] font-black tracking-tight text-white uppercase">RONIN OS</span>
      </div>

      <button
        type="button"
        onClick={onOpenLan}
        className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-[10px] sm:text-[11px] font-mono-tech transition shrink-0 ${
          lanUrl
            ? 'bg-emerald-500/10 hover:bg-emerald-500/20 border-emerald-500/30 text-emerald-300'
            : 'bg-white/[0.03] hover:bg-white/[0.06] border-white/[0.1] text-zinc-400'
        }`}
        title={lanUrl ? 'Ver enlace para abrir en tu móvil por Wi-Fi' : 'El backend no informó una IP de LAN'}
        aria-label={lanUrl ? `Enlace LAN ${lanUrl}` : 'Enlace LAN sin detectar'}
      >
        <span className={`w-1.5 h-1.5 rounded-full ${lanUrl ? 'bg-emerald-400 animate-pulse' : 'bg-zinc-500'}`} />
        <span>
          LAN:{' '}
          <b className="text-white tabular-nums">{lanUrl ? lanUrl.replace('http://', '') : 'sin detectar'}</b>
        </span>
      </button>

      <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white/[0.03] border border-white/[0.08] text-[11px] font-mono-tech text-zinc-300 shrink-0">
        <span className={`w-1.5 h-1.5 rounded-full ${coreStatus === 'CONECTADO' ? 'bg-emerald-400 animate-pulse' : coreStatus === 'FALLA' ? 'bg-rose-500' : 'bg-zinc-500'}`} />
        <span>
          Core:{' '}
          {coreStatus === 'CONECTADO' ? (
            <><b className="text-emerald-400">CONECTADO</b> <span className="text-zinc-300">(OpenCode + Vertex)</span></>
          ) : coreStatus === 'FALLA' ? (
            <><b className="text-rose-400">FALLA</b> <span className="text-zinc-300">(OpenCode / Vertex)</span></>
          ) : (
            <b className="text-zinc-400">SIN VERIFICAR</b>
          )}
        </span>
      </div>

      {vertexProjectId && (
        <div
          className="hidden xl:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white/[0.03] border border-white/[0.08] text-[10px] font-mono-tech text-zinc-400 shrink-0 max-w-[240px]"
          title={`Vertex ${vertexProjectId}${vertexModel ? ` / ${vertexModel}` : ''}`}
        >
          <span className="truncate">Vertex: {vertexProjectId}</span>
        </div>
      )}
    </div>

    <div className="flex items-center gap-1.5 shrink-0">
      <button
        type="button"
        onClick={onRefresh}
        disabled={loading}
        aria-label="Sincronizar datos del sistema"
        className="px-2.5 py-1 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] text-zinc-300 border border-white/[0.08] transition flex items-center gap-1.5 text-[11px] font-mono-tech focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white/50"
      >
        <svg className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-[#E07A5F]' : 'text-zinc-400'}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true"><path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" /></svg>
        <span className="hidden sm:inline uppercase tracking-wider">{loading ? 'Syncing...' : 'Sync OS'}</span>
      </button>
    </div>
  </header>
);
