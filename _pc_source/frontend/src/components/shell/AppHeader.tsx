import React from 'react';
import { Icon } from '../ui/Icon';
import { Tip } from '../ui/Tooltip';
import { compact, num, usd } from '../../utils/format';
import { NAV_BY_ID, type NavTabId } from './nav';
import { MobileBrand } from './MobileDock';

export type CoreStatus = 'CONECTADO' | 'FALLA' | 'SIN_VERIFICAR';

export interface LiveKpis {
  sales: number;
  revenue: number;
  impressions: number;
  hasData: boolean;
  demo: boolean;
  loading: boolean;
}

interface Props {
  activeTab: NavTabId;
  kpis: LiveKpis;
  onOpenPalette: () => void;
  onRefresh: () => void;
  onOpenLan: () => void;
  lanUrl: string;
}

const HeaderStat: React.FC<{ label: string; value: string; tone?: 'accent' | 'ink' }> = ({ label, value, tone = 'ink' }) => (
  <div className="px-3 first:pl-0 last:pr-0">
    <p className="text-[9.5px] leading-none text-ink3">{label}</p>
    <p className={`num mt-1 text-[12.5px] leading-none ${tone === 'accent' ? 'text-accent' : 'text-ink'}`}>{value}</p>
  </div>
);

/** Header de trabajo: contexto, KPIs en vivo, paleta (⌘K), LAN y sincronización. */
export const AppHeader: React.FC<Props> = ({ activeTab, kpis, onOpenPalette, onRefresh, onOpenLan, lanUrl }) => {
  const item = NAV_BY_ID[activeTab];
  return (
    <header className="sticky top-0 z-30 border-b border-line bg-[#0a0a0c]/92 backdrop-blur-xl">
      <div className="flex h-[54px] items-center gap-2 px-3 sm:px-5">
        <div className="lg:hidden">
          <MobileBrand />
        </div>
        <nav aria-label="Ubicación" className="hidden min-w-0 items-center gap-1.5 text-[11.5px] lg:flex">
          <span className="text-ink3">Ronin OS</span>
          <Icon name="chevron-right" size={11} className="text-ink3" />
          <span className="truncate font-medium text-ink">{item.label}</span>
        </nav>

        <div className="ml-auto flex items-center gap-1.5 sm:gap-2.5">
          <span
            className={`chip hidden border-transparent px-1.5 md:inline-flex ${
              kpis.demo ? 'bg-warn/10 text-warn' : kpis.hasData ? 'bg-pos/10 text-pos' : 'bg-panel3 text-ink3'
            }`}
            title={kpis.demo ? 'Modo demo: cifras ficticias etiquetadas' : kpis.hasData ? 'Datos reales registrados' : 'Sin datos reales todavía'}
          >
            {kpis.demo ? 'demo' : kpis.hasData ? 'datos reales' : 'sin datos'}
          </span>

          <div className="hidden items-center divide-x divide-line md:flex">
            <HeaderStat label="Ventas" value={num(kpis.sales)} />
            <HeaderStat label="Ingresos" value={usd(kpis.revenue)} tone="accent" />
            <HeaderStat label="Impr." value={compact(kpis.impressions)} />
          </div>

          <button
            type="button"
            onClick={onOpenPalette}
            className="btn hidden h-8 w-[196px] justify-between px-2.5 text-[11.5px] text-ink3 sm:flex"
            aria-label="Abrir paleta de comandos"
          >
            <span className="flex items-center gap-1.5">
              <Icon name="search" size={13} />
              Buscar o ejecutar
            </span>
            <kbd className="rounded border border-line bg-panel2 px-1 py-0.5 text-[9.5px] text-ink3">Ctrl K</kbd>
          </button>
          <button type="button" onClick={onOpenPalette} aria-label="Buscar" className="btn btn-ghost btn-icon sm:hidden">
            <Icon name="search" size={17} />
          </button>

          <Tip label={lanUrl ? `Móvil LAN: ${lanUrl.replace('http://', '')}` : 'LAN sin detectar'} side="top">
            <button
              type="button"
              onClick={onOpenLan}
              aria-label="Acceso móvil LAN"
              className="btn btn-ghost btn-icon hidden sm:inline-flex"
            >
              <Icon name="wifi" size={16} className={lanUrl ? 'text-pos' : 'text-ink3'} />
            </button>
          </Tip>

          <Tip label="Sincronizar datos" side="top">
            <button
              type="button"
              onClick={onRefresh}
              disabled={kpis.loading}
              aria-label="Sincronizar datos"
              className="btn btn-ghost btn-icon"
            >
              <Icon name="refresh" size={16} className={kpis.loading ? 'animate-spin text-accent' : 'text-ink2'} />
            </button>
          </Tip>

          <img
            src="/generated_images/ron_avatar_profile.png"
            alt="Ron"
            className="ml-0.5 h-[26px] w-[26px] rounded-full border border-line object-cover"
          />
        </div>
      </div>
    </header>
  );
};
