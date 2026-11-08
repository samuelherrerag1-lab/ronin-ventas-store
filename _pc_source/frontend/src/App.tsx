import React, { useEffect, useMemo, useState } from 'react';
import { ErrorBoundary } from './components/ErrorBoundary';
import { LanAccessModal } from './components/LanAccessModal';
import { Sidebar, type NavTabId } from './components/Sidebar';
import { TopHudHeader, type CoreStatus } from './components/TopHudHeader';
import { BaitStudioView } from './components/bait/BaitStudioView';
import { IdentityStudioView } from './components/brand/IdentityStudioView';
import { CatalogFactoryView } from './components/catalog/CatalogFactoryView';
import { CustomizationsHubView } from './components/customizations/CustomizationsHubView';
import { MetricsRadarView } from './components/metrics/MetricsRadarView';
import { PinterestCloneView } from './components/pinterest/PinterestCloneView';
import { PublishCenterView } from './components/publish/PublishCenterView';
import { StanAndStealthView } from './components/stan/StanAndStealthView';
import { ThreadsCloneView } from './components/threads/ThreadsCloneView';
import { useSystemData } from './hooks/useSystemData';

const TABS: NavTabId[] = [
  'threads_clone',
  'pinterest_clone',
  'bait_studio',
  'catalog_factory',
  'publish_center',
  'stan_and_stealth',
  'metrics_radar',
  'brand_identity',
  'customizations_hub',
];

export const App: React.FC = () => {
  const getInitialTab = (): NavTabId => {
    if (typeof window !== 'undefined') {
      const hash = window.location.hash.replace('#', '') as NavTabId;
      if (TABS.includes(hash)) return hash;
      const query = new URLSearchParams(window.location.search).get('tab') as NavTabId;
      if (TABS.includes(query)) return query;
    }
    return 'threads_clone';
  };
  const [activeTab, setActiveTabState] = useState<NavTabId>(getInitialTab);
  const [includeBenchmarks, setIncludeBenchmarks] = useState<boolean>(true);
  const [showLanModal, setShowLanModal] = useState<boolean>(false);

  const setActiveTab = (tab: NavTabId) => {
    setActiveTabState(tab);
    if (typeof window !== 'undefined') window.location.hash = tab;
  };

  const data = useSystemData(() => setActiveTab('threads_clone'));

  useEffect(() => {
    if (typeof window !== 'undefined') window.location.hash = activeTab;
  }, [activeTab]);

  const connectors = data.customizations?.connectors ?? [];
  const verified = connectors.filter((c) => Boolean(c.checked_at));
  const opencode = connectors.find((c) => c.connector_id === 'opencode_v2');
  const vertex = connectors.find((c) => c.connector_id === 'vertex_ai');
  const connectedCount = connectors.filter((c) => c.status === 'CONECTADO').length;
  const failCount = connectors.filter((c) => c.status === 'FALLA').length;
  const coreStatus: CoreStatus = useMemo(() => {
    if (verified.length === 0) return 'SIN_VERIFICAR';
    if (opencode?.status === 'CONECTADO' && vertex?.status === 'CONECTADO') return 'CONECTADO';
    if (opencode?.status === 'FALLA' || vertex?.status === 'FALLA') return 'FALLA';
    return 'SIN_VERIFICAR';
  }, [verified.length, opencode?.status, vertex?.status]);
  const ssoStatus: CoreStatus =
    verified.length === 0
      ? 'SIN_VERIFICAR'
      : failCount > 0
        ? 'FALLA'
        : connectedCount === connectors.length
          ? 'CONECTADO'
          : 'SIN_VERIFICAR';

  return (
    <div className="min-h-screen bg-[#07070b] bg-[radial-gradient(900px_500px_at_18%_-10%,rgba(16,185,129,0.06),transparent_60%),radial-gradient(800px_450px_at_92%_0%,rgba(224,122,95,0.06),transparent_58%)] text-zinc-100 flex flex-col lg:flex-row font-ui">
      <Sidebar
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        totalSkus={data.products.length}
        connectedCount={connectedCount}
        totalConnectors={connectors.length}
        ssoStatus={ssoStatus}
        finopsSpent={data.customizations?.finops?.total_spent_usd ?? 0}
        finopsLimit={data.customizations?.finops?.circuit_breaker_limit_usd ?? 0}
        lanUrl={data.lanUrl}
      />

      <main className="flex-1 min-w-0 min-h-screen lg:h-screen lg:overflow-y-auto flex flex-col pb-24 lg:pb-4">
        <TopHudHeader
          lanUrl={data.lanUrl}
          coreStatus={coreStatus}
          vertexProjectId={data.customizations?.finops?.project_id ?? data.health?.vertex?.project_id ?? null}
          vertexModel={data.health?.vertex?.model ?? null}
          loading={data.loading}
          onRefresh={() => void data.loadAll()}
          onOpenLan={() => setShowLanModal(true)}
        />

        {(data.loadError || data.actionError) && (
          <div className="mx-2.5 sm:mx-5 mt-2.5 space-y-1.5">
            {data.loadError && (
              <div role="alert" className="p-2.5 rounded-xl bg-amber-950/30 border border-amber-500/40 text-[11px] text-amber-200 flex items-start justify-between gap-2">
                <span className="leading-relaxed break-words">Datos incompletos: {data.loadError}</span>
                <button type="button" onClick={() => void data.loadAll()} className="shrink-0 px-2 py-0.5 rounded bg-amber-500/20 border border-amber-500/40 font-mono-tech font-bold">Reintentar</button>
              </div>
            )}
            {data.actionError && (
              <div role="alert" className="p-2.5 rounded-xl bg-rose-950/40 border border-rose-500/40 text-[11px] text-rose-200 flex items-start justify-between gap-2">
                <span className="leading-relaxed break-words">{data.actionError}</span>
                <button type="button" onClick={data.clearActionError} className="shrink-0 px-2 py-0.5 rounded bg-rose-500/20 border border-rose-500/40 font-mono-tech font-bold">Cerrar</button>
              </div>
            )}
          </div>
        )}

        <div className="flex-1 p-2.5 sm:p-5 max-w-full overflow-x-hidden">
          <ErrorBoundary>
            {activeTab === 'threads_clone' && (
              <ThreadsCloneView threads={data.threads} onMutateHook={data.mutateHook} onToggleStatus={data.toggleThread} loading={data.loading} />
            )}
            {activeTab === 'pinterest_clone' && (
              <PinterestCloneView pins={data.pins} includeBenchmarks={includeBenchmarks} onToggleBenchmarks={() => setIncludeBenchmarks((b) => !b)} onToggleStatus={data.togglePin} loading={data.loading} />
            )}
            {activeTab === 'bait_studio' && (
              <BaitStudioView
                onCreateBaitPost={data.createBait}
                onGenerateVertex={data.generateVertex}
                finops={data.customizations?.finops}
                vertexModel={data.health?.vertex?.model ?? data.customizations?.connectors?.find((c) => c.connector_id === 'vertex_ai')?.detail ?? null}
                vertexRegion={data.health?.vertex?.location ?? null}
                availableSkus={data.products.map((p) => ({ sku_id: p.sku_id, title: `${p.sku_id} — ${p.title} ($${p.price_usd})` }))}
              />
            )}
            {activeTab === 'catalog_factory' && (
              <CatalogFactoryView products={data.products} onToggleStan={data.toggleStan} />
            )}
            {activeTab === 'publish_center' && (
              <PublishCenterView products={data.products} onRefreshCatalog={() => void data.loadCatalog()} />
            )}
            {activeTab === 'stan_and_stealth' && (
              <StanAndStealthView products={data.products} stealthDiagnostic={data.customizations?.stealth_Diagnostic} competitorTeardowns={data.customizations?.competitor_teardowns} />
            )}
            {activeTab === 'metrics_radar' && (
              <MetricsRadarView products={data.products} lanUrl={data.lanUrl} onMutateHook={data.mutateHook} onNavigateTab={setActiveTab} />
            )}
            {activeTab === 'brand_identity' && <IdentityStudioView />}
            {activeTab === 'customizations_hub' && (
              <CustomizationsHubView overview={data.customizations} onConnect={data.connect} onToggleSkill={data.toggleSkillById} />
            )}
          </ErrorBoundary>
        </div>
      </main>

      {showLanModal && <LanAccessModal lanUrl={data.lanUrl} onClose={() => setShowLanModal(false)} />}
    </div>
  );
};

export default App;
