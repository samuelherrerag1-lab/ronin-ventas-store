import React from 'react';
import type { SiteManifest } from '../../types/domain';
import { InlineError, PendingNotice, Section, StoreIcon, ExternalIcon } from './publishUi';

interface Props {
  exporting: boolean;
  exportError: string | null;
  exportPending: boolean;
  exportResult: SiteManifest | null;
  manifest: SiteManifest | null;
  manifestLoading: boolean;
  manifestError: string | null;
  manifestPending: boolean;
  onExport: () => void;
  onRetryManifest: () => void;
}

const ManifestSummary: React.FC<{ manifest: SiteManifest; title: string }> = ({ manifest, title }) => (
  <div className="space-y-1.5">
    <div className="text-[10px] uppercase tracking-wider text-zinc-400 font-mono-tech font-bold">{title}</div>
    <dl className="grid grid-cols-2 sm:grid-cols-4 gap-1.5 text-[11px] font-mono-tech tabular-nums">
      <div className="bg-black/40 border border-white/[0.06] rounded-lg px-2 py-1">
        <dt className="text-[9px] text-zinc-500 uppercase">SKUs</dt>
        <dd className="text-zinc-100 font-bold">{manifest.skus ?? '—'}</dd>
      </div>
      <div className="bg-black/40 border border-white/[0.06] rounded-lg px-2 py-1">
        <dt className="text-[9px] text-zinc-500 uppercase">Rutas</dt>
        <dd className="text-zinc-100 font-bold">{Array.isArray(manifest.routes) ? manifest.routes.length : manifest.routes ?? '—'}</dd>
      </div>
      <div className="bg-black/40 border border-white/[0.06] rounded-lg px-2 py-1">
        <dt className="text-[9px] text-zinc-500 uppercase">Archivos</dt>
        <dd className="text-zinc-100 font-bold">{manifest.files ?? '—'}</dd>
      </div>
      <div className="bg-black/40 border border-white/[0.06] rounded-lg px-2 py-1">
        <dt className="text-[9px] text-zinc-500 uppercase">Generado</dt>
        <dd className="text-zinc-300 text-[9px] break-all">{manifest.generated_at ?? '—'}</dd>
      </div>
    </dl>
    {manifest.base_url && (
      <div className="text-[10px] text-zinc-400 font-mono-tech break-all">base_url: {manifest.base_url}</div>
    )}
    {Array.isArray(manifest.blockers) && manifest.blockers.length > 0 && (
      <div className="text-[10px] text-amber-300 leading-relaxed">
        Bloqueos del sitio: {manifest.blockers.join(', ')}
      </div>
    )}
  </div>
);

export const PublishExportPanel: React.FC<Props> = ({
  exporting,
  exportError,
  exportPending,
  exportResult,
  manifest,
  manifestLoading,
  manifestError,
  manifestPending,
  onExport,
  onRetryManifest,
}) => (
  <Section
    title="Sitio estático publicable"
    subtitle="Genera /store/ con la tienda y las rutas puente. El enlace se abre en este mismo equipo o en la LAN."
  >
    <div className="flex flex-wrap items-center gap-2">
      <button
        type="button"
        onClick={onExport}
        disabled={exporting}
        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#E07A5F] hover:bg-[#ea8a70] text-black text-[11px] font-mono-tech font-bold transition disabled:opacity-50"
      >
        <StoreIcon className="w-4 h-4" />
        {exporting ? 'Exportando...' : 'Exportar sitio estático'}
      </button>
      <a
        href="/store/"
        target="_blank"
        rel="noreferrer"
        className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.1] text-[11px] font-mono-tech text-zinc-200 transition"
      >
        Abrir /store/
        <ExternalIcon />
      </a>
      <button
        type="button"
        onClick={onRetryManifest}
        disabled={manifestLoading}
        className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.1] text-[11px] font-mono-tech text-zinc-200 transition disabled:opacity-50"
      >
        {manifestLoading ? 'Leyendo...' : 'Leer manifest'}
      </button>
    </div>

    {exportPending && <PendingNotice endpoint="/api/publish/export-site" />}
    {!exportPending && exportError && <InlineError message={exportError} onRetry={onExport} />}
    {exportResult && <ManifestSummary manifest={exportResult} title="Resultado de la exportación" />}

    {manifestPending && <PendingNotice endpoint="/api/publish/site-manifest" onRetry={onRetryManifest} />}
    {!manifestPending && manifestError && <InlineError message={manifestError} onRetry={onRetryManifest} />}
    {!manifestPending && !manifestError && manifest && (
      <ManifestSummary manifest={manifest} title="Manifest en disco" />
    )}
    {!manifestPending && !manifestError && !manifest && !manifestLoading && (
      <div className="p-2.5 rounded-xl bg-black/40 border border-white/[0.06] text-[11px] text-zinc-500 leading-relaxed">
        Todavía no hay manifest de sitio. Ejecuta la exportación para generarlo.
      </div>
    )}
  </Section>
);
