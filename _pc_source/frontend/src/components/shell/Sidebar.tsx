import React from 'react';
import type { CoreStatus } from './AppHeader';
import { BrandMark } from '../ui/BrandMark';
import { Icon } from '../ui/Icon';
import { Tip } from '../ui/Tooltip';
import { GROUPS, NAV_ITEMS, type NavTabId } from './nav';

export interface ShellStatus {
  totalSkus: number;
  connectedCount: number;
  totalConnectors: number;
  coreStatus: CoreStatus;
  finopsSpent: number;
  finopsLimit: number;
  lanUrl: string;
}

interface Props {
  activeTab: NavTabId;
  onSelectTab: (tab: NavTabId) => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
  status: ShellStatus;
  badges: Partial<Record<NavTabId, string>>;
  onOpenLan: () => void;
}

const statusTone = (status: CoreStatus): 'pos' | 'neg' | 'mute' =>
  status === 'CONECTADO' ? 'pos' : status === 'FALLA' ? 'neg' : 'mute';

const NavButton: React.FC<{
  active: boolean;
  label: string;
  icon: React.ReactNode;
  badge?: string;
  collapsed: boolean;
  onClick: () => void;
  action?: boolean;
}> = ({ active, label, icon, badge, collapsed, onClick, action }) => {
  const button = (
    <button
      type="button"
      onClick={onClick}
      aria-current={active ? 'page' : undefined}
      aria-label={collapsed ? label : undefined}
      className={`group relative flex h-[34px] w-full items-center gap-2.5 rounded-ctl border px-2.5 text-[12.5px] transition-colors duration-150 ${
        active
          ? 'border-line2 bg-panel2 text-ink'
          : 'border-transparent text-ink2 hover:bg-panel2/70 hover:text-ink'
      } ${collapsed ? 'justify-center px-0' : ''}`}
    >
      <span className={`shrink-0 ${active ? 'text-accent' : 'text-ink3 group-hover:text-ink2'}`}>{icon}</span>
      {!collapsed && <span className="min-w-0 flex-1 truncate text-left">{label}</span>}
      {!collapsed && badge && (
        <span
          className={`chip shrink-0 border-transparent px-1.5 ${
            action ? 'bg-accent/10 text-accent' : 'bg-panel3 text-ink3'
          }`}
        >
          {badge}
        </span>
      )}
      {collapsed && action && <span className="dot absolute right-2 top-2 bg-accent" aria-hidden="true" />}
    </button>
  );
  return collapsed ? (
    <Tip label={label} side="right" className="w-full">
      {button}
    </Tip>
  ) : (
    button
  );
};

/** Navegación de escritorio: icono + etiqueta, colapsable a riel con tooltip. */
export const Sidebar: React.FC<Props> = ({
  activeTab,
  onSelectTab,
  collapsed,
  onToggleCollapse,
  status,
  badges,
  onOpenLan,
}) => {
  const ratio = Math.min(100, (status.finopsSpent / Math.max(0.01, status.finopsLimit)) * 100);
  return (
    <aside
      className={`sticky top-0 hidden h-screen shrink-0 flex-col border-r border-line bg-[#0b0b0d] lg:flex ${
        collapsed ? 'w-[62px]' : 'w-[236px]'
      } transition-[width] duration-220`}
      aria-label="Navegación principal"
    >
      <div className={`flex h-[54px] items-center border-b border-line ${collapsed ? 'justify-center' : 'justify-between px-3'}`}>
        <button
          type="button"
          onClick={() => onSelectTab('home')}
          className="flex min-w-0 items-center gap-2 rounded-ctl px-0.5 py-1 text-left"
          aria-label="Ronin Ventas OS — ir al Command Center"
        >
          <BrandMark size={24} className="shrink-0 text-ink" />
          {!collapsed && (
            <span className="min-w-0">
              <span className="font-display block truncate text-[13px] font-bold leading-tight tracking-[-0.02em] text-ink">
                Ronin OS
              </span>
              <span className="block truncate text-[10px] leading-tight text-ink3">@ronOverthinks</span>
            </span>
          )}
        </button>
        {!collapsed && (
          <Tip label="Colapsar navegación" side="top">
            <button
              type="button"
              onClick={onToggleCollapse}
              aria-label="Colapsar navegación"
              className="btn btn-ghost btn-icon"
            >
              <Icon name="chevron-left" size={15} />
            </button>
          </Tip>
        )}
      </div>

      <nav className="scroll-thin flex-1 px-2 py-2">
        {GROUPS.map((group) => (
          <div key={group} className="mb-3 last:mb-0">
            {!collapsed ? (
              <p className="px-2 pb-1 pt-2 text-[10.5px] text-ink3">{group}</p>
            ) : (
              <div className="mx-auto my-2 h-px w-5 bg-line" aria-hidden="true" />
            )}
            <div className="space-y-0.5">
              {NAV_ITEMS.filter((item) => item.group === group).map((item) => (
                <NavButton
                  key={item.id}
                  active={activeTab === item.id}
                  label={item.label}
                  icon={<Icon name={item.icon} size={16} />}
                  badge={badges[item.id]}
                  action={item.id === 'metrics_radar' || item.id === 'publish_center'}
                  collapsed={collapsed}
                  onClick={() => onSelectTab(item.id)}
                />
              ))}
            </div>
          </div>
        ))}
      </nav>

      <div className="border-t border-line p-2">
        {collapsed ? (
          <div className="flex flex-col items-center gap-2 py-1">
            <Tip label={`Core: ${status.coreStatus}`} side="right">
              <span className="flex h-7 w-full items-center justify-center">
                <span className={`dot ${statusTone(status.coreStatus) === 'pos' ? 'bg-pos' : statusTone(status.coreStatus) === 'neg' ? 'bg-neg' : 'bg-ink3'}`} />
              </span>
            </Tip>
            <Tip label={`${status.connectedCount}/${status.totalConnectors} conectores`} side="right">
              <span className="flex h-7 w-full items-center justify-center text-[10px] text-ink2">
                {status.connectedCount}/{status.totalConnectors}
              </span>
            </Tip>
            <Tip label="Expandir navegación" side="right">
              <button type="button" onClick={onToggleCollapse} aria-label="Expandir navegación" className="btn btn-ghost btn-icon">
                <Icon name="chevron-right" size={15} />
              </button>
            </Tip>
          </div>
        ) : (
          <div className="space-y-2">
            <div className="rounded-ctl border border-line bg-panel px-2.5 py-2">
              <div className="flex items-center justify-between gap-2">
                <span className="text-[11px] text-ink2">Core</span>
                <span className="chip border-transparent bg-panel3 px-1.5 text-[10px]">
                  <span className={`dot ${statusTone(status.coreStatus) === 'pos' ? 'bg-pos' : statusTone(status.coreStatus) === 'neg' ? 'bg-neg' : 'bg-ink3'}`} />
                  {status.coreStatus === 'CONECTADO' ? 'conectado' : status.coreStatus === 'FALLA' ? 'falla' : 'sin verificar'}
                </span>
              </div>
              <div className="mt-1.5 flex items-center justify-between text-[11px] text-ink3">
                <span>Catálogo</span>
                <span className="num text-ink2">{status.totalSkus} SKU</span>
              </div>
              <div className="mt-0.5 flex items-center justify-between text-[11px] text-ink3">
                <span>Conectores</span>
                <span className="num text-ink2">
                  {status.connectedCount}/{status.totalConnectors}
                </span>
              </div>
            </div>

            <div className="rounded-ctl border border-line bg-panel px-2.5 py-2">
              <div className="flex items-baseline justify-between text-[11px]">
                <span className="text-ink2">Vertex</span>
                <span className="num text-[10px] text-ink3">
                  ${status.finopsSpent.toFixed(2)} / ${status.finopsLimit.toFixed(2)}
                </span>
              </div>
              <div className="mt-1.5 h-[3px] w-full overflow-hidden rounded-full bg-panel3">
                <div className="h-full rounded-full bg-accent/80" style={{ width: `${ratio}%` }} />
              </div>
            </div>

            <button
              type="button"
              onClick={onOpenLan}
              className="btn btn-ghost h-auto w-full justify-start px-2.5 py-1.5 text-[11px]"
            >
              <Icon name="wifi" size={13} className={status.lanUrl ? 'text-pos' : 'text-ink3'} />
              <span className="mono-id truncate text-ink2">{status.lanUrl ? status.lanUrl.replace('http://', '') : 'LAN sin detectar'}</span>
            </button>
          </div>
        )}
      </div>
    </aside>
  );
};
