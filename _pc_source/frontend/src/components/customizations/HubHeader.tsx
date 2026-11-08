import React from 'react';
import { BoltIcon, GlobalRing, Spinner, cx } from './HubBits';

export type HubTab = 'connectors' | 'skills';

export interface HubHeaderProps {
  activeTab: HubTab;
  onSelectTab: (tab: HubTab) => void;
  connectorsCount: number;
  skillsCount: number;
  connectedCount: number;
  failCount: number;
  isRunningAll: boolean;
  onRunAll: () => void;
  finopsSpent: number;
  finopsLimit: number;
  ledgerFound: boolean;
  projectId?: string | null;
}

export const HubHeader: React.FC<HubHeaderProps> = ({
  activeTab,
  onSelectTab,
  connectorsCount,
  skillsCount,
  connectedCount,
  failCount,
  isRunningAll,
  onRunAll,
  finopsSpent,
  finopsLimit,
  ledgerFound,
  projectId,
}) => {
  const tabs: Array<{ id: HubTab; label: string; count: number }> = [
    { id: 'connectors', label: 'Conexiones', count: connectorsCount },
    { id: 'skills', label: 'Skills', count: skillsCount },
  ];

  return (
    <header className="border-b border-white/[0.07] pb-5">
      <div className="flex items-center justify-between gap-4">
        <div className="min-w-0">
          <p className="flex items-center gap-2 text-[11px] uppercase tracking-[0.14em] text-zinc-400">
            <span className="h-1 w-1 rounded-full bg-[#E07A5F]" />
            <span className="truncate">
              Ronin OS<span className="hidden sm:inline"> · Customizations</span>
            </span>
          </p>
          <h1 className="mt-1.5 font-grotesque text-[24px] font-semibold leading-none text-white">
            Conexiones
          </h1>
        </div>

        <div className="flex shrink-0 items-center gap-2.5">
          <GlobalRing connected={connectedCount} total={connectorsCount} failing={failCount} />
          <button
            type="button"
            onClick={onRunAll}
            disabled={isRunningAll}
            aria-label="Ejecutar diagnóstico completo de conexiones"
            className="flex h-10 items-center gap-2 rounded-xl bg-white px-3.5 text-[12px] font-medium text-[#0b0c0e] transition-colors duration-150 ease-out hover:bg-zinc-200 disabled:cursor-wait disabled:opacity-70"
          >
            {isRunningAll ? <Spinner className="h-3.5 w-3.5" /> : <BoltIcon className="h-3.5 w-3.5" />}
            <span>{isRunningAll ? 'Diagnosticando' : 'Diagnóstico'}</span>
          </button>
        </div>
      </div>

      <div className="mt-5 flex flex-wrap items-center justify-between gap-3">
        <div className="flex rounded-xl border border-white/[0.07] bg-white/[0.025] p-1" role="tablist" aria-label="Secciones del hub">
          {tabs.map((tab) => {
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                role="tab"
                aria-selected={active}
                onClick={() => onSelectTab(tab.id)}
                className={cx(
                  'flex h-8 items-center gap-2 rounded-lg px-3 text-[12px] transition-colors duration-150 ease-out',
                  active ? 'bg-white/[0.09] text-white' : 'text-zinc-400 hover:text-zinc-200',
                )}
              >
                {tab.label}
                <span className={cx('font-mono-tech text-[11px] tabular-nums', active ? 'text-zinc-400' : 'text-zinc-400/80')}>
                  {tab.count}
                </span>
              </button>
            );
          })}
        </div>

        <p
          className="hidden items-center gap-2 text-[11px] text-zinc-400 sm:flex"
          title={ledgerFound ? 'Ledger de costos detectado' : 'Ledger no encontrado: se usan valores por defecto'}
        >
          <span className="h-1 w-1 rounded-full bg-zinc-600" />
          <span>Presupuesto IA</span>
          <span className="font-mono-tech tabular-nums text-zinc-400">
            ${finopsSpent.toFixed(2)} / ${finopsLimit.toFixed(2)}
          </span>
          <span className="max-w-[170px] truncate font-mono-tech text-[10px] text-zinc-500" title={projectId ?? 'Proyecto Vertex sin verificar'}>
            {projectId ?? 'proyecto sin verificar'}
          </span>
        </p>
      </div>
    </header>
  );
};
