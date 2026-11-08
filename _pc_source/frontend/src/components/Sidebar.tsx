import React from 'react';

export type NavTabId =
  | 'threads_clone'
  | 'pinterest_clone'
  | 'bait_studio'
  | 'catalog_factory'
  | 'publish_center'
  | 'stan_and_stealth'
  | 'metrics_radar'
  | 'brand_identity'
  | 'customizations_hub';

interface SidebarProps {
  activeTab: NavTabId;
  onSelectTab: (tab: NavTabId) => void;
  totalSkus: number;
  connectedCount: number;
  totalConnectors: number;
  ssoStatus?: 'CONECTADO' | 'FALLA' | 'SIN_VERIFICAR';
  finopsSpent: number;
  finopsLimit: number;
  lanUrl?: string;
}

const MetaBadge = () => (
  <svg className="w-3.5 h-3.5 text-[#0095F6] inline fill-current shrink-0" viewBox="0 0 24 24">
    <path d="M10.067.87a2.89 2.89 0 0 1 3.866 0l1.197 1.054a2.89 2.89 0 0 0 2.219.72l1.58-.152a2.89 2.89 0 0 1 3.128 2.272l.37 1.547a2.89 2.89 0 0 0 1.42 1.867l1.378.783a2.89 2.89 0 0 1 1.434 3.593l-.565 1.49a2.89 2.89 0 0 0 0 2.348l.565 1.49a2.89 2.89 0 0 1-1.434 3.593l-1.378.783a2.89 2.89 0 0 0-1.42 1.867l-.37 1.547a2.89 2.89 0 0 1-3.128 2.272l-1.58-.152a2.89 2.89 0 0 0-2.219-.72l-1.197 1.054a2.89 2.89 0 0 1-3.866 0l-1.197-1.054a2.89 2.89 0 0 0-2.219-.72l-1.58.152a2.89 2.89 0 0 1-3.128-2.272l-.37-1.547a2.89 2.89 0 0 0-1.42-1.867l-1.378-.783a2.89 2.89 0 0 1-1.434-3.593l.565-1.49a2.89 2.89 0 0 0 0-2.348l-.565-1.49a2.89 2.89 0 0 1 1.434-3.593l1.378-.783a2.89 2.89 0 0 0 1.42-1.867l.37-1.547a2.89 2.89 0 0 1 3.128-2.272l1.58.152a2.89 2.89 0 0 0 2.219-.72l1.197-1.054ZM16.67 8.27l-5.656 5.657-2.828-2.829-1.414 1.415 4.242 4.242 7.07-7.07-1.414-1.415Z" />
  </svg>
);

export const NavSvg = ({ id }: { id: NavTabId }) => {
  const cls = 'w-4 h-4 shrink-0';
  if (id === 'threads_clone') {
    return <svg className={cls} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path strokeLinecap="round" strokeLinejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 01.865-.501 48.172 48.172 0 003.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v5.998z" /></svg>;
  }
  if (id === 'pinterest_clone') {
    return <svg className={cls} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z" /></svg>;
  }
  if (id === 'bait_studio') {
    return <svg className={cls} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path strokeLinecap="round" strokeLinejoin="round" d="M10.5 1.5H8.25A2.25 2.25 0 006 3.75v16.5a2.25 2.25 0 002.25 2.25h7.5A2.25 2.25 0 0018 20.25V3.75a2.25 2.25 0 00-2.25-2.25H13.5m-3 0V3h3V1.5m-3 0h3m-3 18.75h3" /></svg>;
  }
  if (id === 'catalog_factory') {
    return <svg className={cls} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path strokeLinecap="round" strokeLinejoin="round" d="M21 7.5l-9-5.25L3 7.5m18 0l-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9" /></svg>;
  }
  if (id === 'publish_center') {
    return <svg className={cls} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path strokeLinecap="round" strokeLinejoin="round" d="M12 3v12m0 0 4-4m-4 4-4-4M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" /></svg>;
  }
  if (id === 'stan_and_stealth') {
    return <svg className={cls} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" /></svg>;
  }
  if (id === 'metrics_radar') {
    return <svg className={cls} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" /></svg>;
  }
  if (id === 'brand_identity') {
    return <svg className={cls} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path strokeLinecap="round" strokeLinejoin="round" d="M12 3c-4.97 0-9 3.582-9 8 0 2.21 1.007 4.21 2.638 5.66-.108.94-.55 2.28-1.638 3.34 1.86.14 3.44-.4 4.6-1.06A10.9 10.9 0 0 0 12 19c4.97 0 9-3.582 9-8s-4.03-8-9-8Z" /><circle cx="9" cy="11" r="1" fill="currentColor" stroke="none" /><circle cx="12" cy="11" r="1" fill="currentColor" stroke="none" /><circle cx="15" cy="11" r="1" fill="currentColor" stroke="none" /></svg>;
  }
  return <svg className={cls} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" /></svg>;
};

export const NAV_ITEMS: { id: NavTabId; label: string; shortLabel: string; badge: string }[] = [
  { id: 'threads_clone', label: 'Clon Threads (1:1)', shortLabel: 'Threads', badge: 'FEED' },
  { id: 'pinterest_clone', label: 'Clon Pinterest (236px)', shortLabel: 'Pinterest', badge: 'GRID' },
  { id: 'bait_studio', label: 'Lab Anzuelos + Vertex', shortLabel: 'iOS Lab', badge: 'NB2' },
  { id: 'catalog_factory', label: 'Fábrica 55 Productos', shortLabel: '55 SKUs', badge: '52+3' },
  { id: 'publish_center', label: 'Centro de Publicación', shortLabel: 'Publicar', badge: 'GO' },
  { id: 'stan_and_stealth', label: 'Stan Clone & Stealth', shortLabel: 'Stan Pro', badge: 'PRO' },
  { id: 'metrics_radar', label: 'Radar Métricas & Ventas', shortLabel: 'Métricas', badge: '14D' },
  { id: 'brand_identity', label: 'Identidad de Marca', shortLabel: 'Marca', badge: 'ID' },
  { id: 'customizations_hub', label: 'Customizations & SSO', shortLabel: 'Vault', badge: 'HUB' },
];

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab, onSelectTab, totalSkus, connectedCount, totalConnectors, ssoStatus, finopsSpent, finopsLimit, lanUrl,
}) => {
  return (
    <>
      {/* Desktop Left Sidebar with Tactical Density */}
      <aside className="hidden lg:flex w-64 bg-[#08090d]/98 backdrop-blur-2xl border-r border-white/[0.08] flex-col justify-between h-screen sticky top-0 select-none shrink-0 font-ui">
        <div>
          <div className="p-3.5 border-b border-white/[0.08]">
            <div className="flex items-center gap-3">
              <div className="relative shrink-0">
                <img
                  src="/generated_images/ron_avatar_profile.png"
                  alt="@ronoverthinks"
                  className="w-10 h-10 rounded-full object-cover ring-2 ring-[#E07A5F]/70 shadow-lg"
                />
                <span className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-emerald-400 rounded-full ring-2 ring-[#08090d] animate-pulse" />
              </div>
              <div className="min-w-0">
                <div className="flex items-center gap-1.5">
                  <span className="font-display text-[11px] font-black tracking-tight text-white uppercase">RONIN OS</span>
                  <span className="text-[8px] px-1.5 py-0.2 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 font-mono-tech font-bold">v2.0</span>
                </div>
                <div className="text-[11px] text-zinc-400 flex items-center gap-1 truncate mt-0.5">
                  <span className="font-medium text-zinc-300">@ronoverthinks</span>
                  <MetaBadge />
                  <span className="text-zinc-600">•</span>
                  <span className="text-[#E07A5F] text-[10px] font-mono-tech font-bold">Ron Solo</span>
                </div>
              </div>
            </div>
          </div>

          <div className="px-2 py-2.5 space-y-1">
            <div className="px-2 pb-1 text-[9px] font-mono-tech font-bold uppercase tracking-[0.12em] text-zinc-500">7 Módulos Grill Oficial</div>
            {NAV_ITEMS.map((item) => {
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  data-tab={item.id}
                  onClick={() => onSelectTab(item.id)}
                  aria-current={isActive ? 'page' : undefined}
                  className={`w-full flex items-center justify-between px-2.5 py-2 rounded-xl text-xs font-medium transition-all focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white/50 ${
                    isActive
                      ? 'bg-white/[0.07] border border-white/15 text-white shadow-[0_1px_0_rgba(255,255,255,0.06)_inset]'
                      : 'text-zinc-400 hover:text-zinc-100 hover:bg-white/[0.03] border border-transparent'
                  }`}
                >
                  <span className="flex items-center gap-2.5 min-w-0">
                    <span className={isActive ? 'text-[#E07A5F]' : 'text-zinc-500'}><NavSvg id={item.id} /></span>
                    <span className="truncate">{item.label}</span>
                  </span>
                  <span className={`text-[8px] px-1.5 py-0.5 rounded font-mono-tech font-bold uppercase tracking-wider shrink-0 ${isActive ? 'bg-[#E07A5F] text-black shadow-sm' : 'bg-white/[0.04] text-zinc-500'}`}>
                    {item.badge}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        <div className="p-3 border-t border-white/[0.08] space-y-2 bg-black/40">
          {lanUrl && (
            <div className="p-2 rounded-xl bg-emerald-950/20 border border-emerald-500/25 text-[10px] font-mono-tech">
              <div className="text-emerald-400 font-bold flex items-center justify-between">
                <span>MÓVIL LAN WI-FI</span>
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
              </div>
              <div className="text-zinc-300 truncate mt-0.5 tabular-nums">{lanUrl}</div>
            </div>
          )}
          <div className="flex items-center justify-between text-xs">
            <span className="text-zinc-400">Catálogo Activo</span>
            <span className="font-mono-tech font-bold text-emerald-400 tabular-nums">{totalSkus} SKUs</span>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-zinc-400">Conectores SSO</span>
            {ssoStatus === 'SIN_VERIFICAR' || (!ssoStatus && connectedCount === 0) ? (
              <span className="font-mono-tech font-bold text-zinc-500">SIN VERIFICAR</span>
            ) : connectedCount > 0 ? (
              <span className="font-mono-tech font-bold text-emerald-400 tabular-nums">{connectedCount}/{totalConnectors} Activos</span>
            ) : (
              <span className="font-mono-tech font-bold text-rose-400 tabular-nums">0/{totalConnectors} FALLA</span>
            )}
          </div>
          <div className="pt-1.5 border-t border-white/[0.06]">
            <div className="flex items-center justify-between text-[11px] text-zinc-400 mb-1">
              <span>Vertex Nano Banana 2</span>
              <span className="text-zinc-200 font-mono-tech text-[10px] tabular-nums">${finopsSpent.toFixed(2)} / ${finopsLimit.toFixed(2)}</span>
            </div>
            <div className="w-full h-1 bg-zinc-800/80 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-emerald-400 to-amber-400" style={{ width: `${Math.min(100, (finopsSpent / Math.max(0.01, finopsLimit)) * 100)}%` }} />
            </div>
          </div>
        </div>
      </aside>

      {/* Mobile Bottom Glass Navigation Dock (< lg) */}
      <nav className="lg:hidden fixed bottom-0 inset-x-0 z-40 bg-[#08090d]/95 backdrop-blur-2xl border-t border-white/[0.1] px-1 py-1.5 flex items-center justify-between gap-0.5 overflow-x-auto no-scrollbar select-none shadow-[0_-10px_30px_rgba(0,0,0,0.85)] font-ui">
        {NAV_ITEMS.map((item) => {
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              data-tab={item.id}
              onClick={() => onSelectTab(item.id)}
              aria-current={isActive ? 'page' : undefined}
              aria-label={item.label}
              className={`flex flex-col items-center justify-center py-1 px-1 rounded-xl min-w-[40px] shrink-0 transition-all focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white/50 ${
                isActive ? 'bg-[#E07A5F]/20 text-[#E07A5F] border border-[#E07A5F]/40' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              <NavSvg id={item.id} />
              <span className="text-[8.5px] font-mono-tech font-bold tracking-tight mt-0.5 truncate max-w-[46px]">{item.shortLabel}</span>
            </button>
          );
        })}
      </nav>
    </>
  );
};
