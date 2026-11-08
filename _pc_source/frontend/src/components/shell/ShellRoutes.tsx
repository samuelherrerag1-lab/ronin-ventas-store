import React from 'react';
import { ErrorBoundary } from '../ErrorBoundary';
import { BaitStudioView } from '../bait/BaitStudioView';
import { IdentityStudioView } from '../brand/IdentityStudioView';
import { CatalogFactoryView } from '../catalog/CatalogFactoryView';
import { CustomizationsHubView } from '../customizations/CustomizationsHubView';
import { HomeView } from '../home/HomeView';
import { MetricsRadarView } from '../metrics/MetricsRadarView';
import { PinterestCloneView } from '../pinterest/PinterestCloneView';
import { PublishCenterView } from '../publish/PublishCenterView';
import { StanAndStealthView } from '../stan/StanAndStealthView';
import { ThreadsCloneView } from '../threads/ThreadsCloneView';
import type { MetricsState } from '../../hooks/useMetrics';
import type { SystemData } from '../../hooks/useSystemData';
import type { NavTabId } from './nav';

interface Props {
  activeTab: NavTabId;
  includeBenchmarks: boolean;
  data: SystemData;
  metrics: MetricsState;
  onNavigate: (tab: NavTabId) => void;
  onToggleBenchmarks: () => void;
}

/** Switch de vistas del `<main>`: una tab activa monta una sola pantalla. */
export const ShellRoutes: React.FC<Props> = ({
  activeTab,
  includeBenchmarks,
  data,
  metrics,
  onNavigate,
  onToggleBenchmarks,
}) => (
  <ErrorBoundary key={activeTab}>
    {activeTab === 'home' && (
      <HomeView
        products={data.products}
        threads={data.threads}
        pins={data.pins}
        customizations={data.customizations}
        metrics={metrics}
        onNavigate={onNavigate}
        onMutateHook={data.mutateHook}
      />
    )}
    {activeTab === 'threads_clone' && (
      <ThreadsCloneView threads={data.threads} onMutateHook={data.mutateHook} onToggleStatus={data.toggleThread} loading={data.loading} />
    )}
    {activeTab === 'pinterest_clone' && (
      <PinterestCloneView pins={data.pins} includeBenchmarks={includeBenchmarks} onToggleBenchmarks={onToggleBenchmarks} onToggleStatus={data.togglePin} loading={data.loading} />
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
      <MetricsRadarView products={data.products} metrics={metrics} lanUrl={data.lanUrl} onMutateHook={data.mutateHook} />
    )}
    {activeTab === 'brand_identity' && <IdentityStudioView />}
    {activeTab === 'customizations_hub' && (
      <CustomizationsHubView overview={data.customizations} onConnect={data.connect} onToggleSkill={data.toggleSkillById} />
    )}
  </ErrorBoundary>
);
