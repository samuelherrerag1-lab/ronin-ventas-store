import React, { useState } from 'react';
import type { ProductSKU, PublishPlatform } from '../../types/domain';
import { CheckoutLinksPanel } from './CheckoutLinksPanel';
import { PublishExportPanel } from './PublishExportPanel';
import { PublishKitPanel } from './PublishKitPanel';
import { PublishReadinessPanel } from './PublishReadinessPanel';
import { usePublishCenter } from './usePublishCenter';

interface Props {
  products: ProductSKU[];
  onRefreshCatalog: () => void;
}

const isReady = (sku: ProductSKU): boolean =>
  sku.checkout_ready ?? Boolean(sku.gumroad_url || sku.hotmart_url);

export const PublishCenterView: React.FC<Props> = ({ products, onRefreshCatalog }) => {
  const [platform, setPlatform] = useState<PublishPlatform>('threads');
  const center = usePublishCenter();

  const paid = products.filter((p) => p.price_usd > 0);
  const ready = paid.filter(isReady);
  const paidCount = paid.length;
  const missing = paidCount - ready.length;
  const kit = center.kits[platform];

  const refreshAll = () => {
    void center.loadAll();
  };

  return (
    <div className="space-y-4 text-zinc-100 font-ui">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3 border-b border-white/[0.08]">
        <div>
          <h1 className="text-lg sm:text-xl font-bold tracking-tight text-white flex items-center gap-2 flex-wrap font-grotesque">
            <span className="px-2 py-0.5 bg-[#E07A5F]/15 text-[#E07A5F] rounded-lg border border-[#E07A5F]/30 text-xs font-mono-tech font-bold">
              PUBLICAR
            </span>
            <span>Centro de Publicación y Checkout</span>
          </h1>
          <p className="text-xs text-zinc-400 mt-0.5 max-w-3xl leading-relaxed">
            Checklist real, cola de contenido, checkout por SKU y exportación del sitio. Todo lo que no existe
            en el backend se marca como pendiente: nunca se simula un resultado.
          </p>
        </div>
        <button
          type="button"
          onClick={refreshAll}
          className="inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.1] text-[11px] font-mono-tech font-bold text-zinc-200 transition self-start sm:self-auto"
        >
          <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" d="M20 11a8 8 0 1 0-2.34 5.66M20 4v7h-7" />
          </svg>
          Reconsultar todo
        </button>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-3">
        <PublishReadinessPanel
          data={center.readiness.data}
          loading={center.readiness.loading}
          error={center.readiness.error}
          pending={center.readiness.pending}
          onRetry={() => void center.loadReadiness()}
          checkoutMissing={missing}
        />
        <PublishExportPanel
          exporting={center.exporting}
          exportError={center.exportError}
          exportPending={center.exportPending}
          exportResult={center.exportResult}
          manifest={center.manifest.data}
          manifestLoading={center.manifest.loading}
          manifestError={center.manifest.error}
          manifestPending={center.manifest.pending}
          onExport={() => void center.runExport()}
          onRetryManifest={() => void center.loadManifest()}
        />
      </div>

      <PublishKitPanel
        platform={platform}
        onChangePlatform={setPlatform}
        items={kit.data}
        loading={kit.loading}
        error={kit.error}
        pending={kit.pending}
        markNote={center.markNote}
        markingId={center.markingId}
        onRetry={() => void center.loadKit(platform)}
        onMark={(item) => void center.markItem(platform, item)}
      />

      <CheckoutLinksPanel
        products={products}
        paidCount={paidCount}
        readyCount={ready.length}
        onSaved={onRefreshCatalog}
      />
    </div>
  );
};
