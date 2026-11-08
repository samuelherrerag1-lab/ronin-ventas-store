import React, { useEffect, useState } from 'react';
import { errorMessage, fetchMetricsSummary, resetMetrics } from '../../api/client';
import type { MetricsSummaryResponse, ProductSKU } from '../../types/domain';
import { copyText } from '../../utils/clipboard';
import { MetricsImportModal } from './MetricsImportModal';

interface Props {
  products: ProductSKU[];
  lanUrl: string;
  onMutateHook: (postId: string) => void;
  onNavigateTab: (tab: any) => void;
}

export const MetricsRadarView: React.FC<Props> = ({ products, lanUrl, onMutateHook, onNavigateTab }) => {
  const [demoMode, setDemoMode] = useState(false);
  const [summary, setSummary] = useState<MetricsSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [copiedLan, setCopiedLan] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [resetError, setResetError] = useState<string | null>(null);

  const loadMetrics = async (demo: boolean) => {
    setLoading(true);
    setLoadError(null);
    try {
      const data = await fetchMetricsSummary(demo);
      setSummary(data);
    } catch (error) {
      setLoadError(errorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadMetrics(demoMode);
  }, [demoMode]);

  const handleReset = async () => {
    if (!window.confirm('¿Confirmas reiniciar todas las métricas reales a cero? Esta acción no se puede deshacer.')) return;
    try {
      await resetMetrics();
      await loadMetrics(false);
    } catch (error) {
      setResetError(errorMessage(error));
    }
  };

  const copyLan = () => {
    void copyText(lanUrl).then(setCopiedLan);
    window.setTimeout(() => setCopiedLan(false), 1600);
  };

  const hasData = summary?.has_real_data ?? false;
  const isDemo = summary?.is_demo_mode ?? false;

  return (
    <div className="space-y-4 text-zinc-100 pb-8 font-ui">
      {/* Header with Title and Mode Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3 border-b border-white/[0.08]">
        <div>
          <h1 className="text-lg sm:text-xl font-bold tracking-tight text-white flex items-center gap-2 flex-wrap font-grotesque">
            <span className="px-2 py-0.5 bg-emerald-500/15 text-emerald-400 rounded-lg border border-emerald-500/30 text-xs font-mono-tech font-bold">RADAR 14D</span>
            <span>Métricas, Ventas & Criterio &quot;Doblar o Matar&quot;</span>
          </h1>
          <p className="text-xs text-zinc-400 mt-0.5">Telemetría real: Leading (Impresiones/CTR/Saves) + Lagging (Gumroad USD / Hotmart COP / Ventas).</p>
        </div>

        <div className="flex items-center gap-2 flex-wrap font-mono-tech text-xs">
          <label className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-black/70 border border-white/10 cursor-pointer select-none">
            <input type="checkbox" checked={demoMode} onChange={(e) => setDemoMode(e.target.checked)} className="rounded border-zinc-700 text-[#E07A5F]" />
            <span className={demoMode ? 'text-amber-300 font-bold' : 'text-zinc-400'}>MODO DEMO</span>
          </label>
          <button onClick={() => setShowModal(true)} className="px-3 py-1 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-black font-bold transition">
            + Importar / Registrar
          </button>
          {hasData && !isDemo && (
            <button type="button" aria-label="Reiniciar métricas reales a cero" onClick={handleReset} className="px-2.5 py-1 rounded-lg bg-white/[0.04] hover:bg-rose-950/60 text-zinc-400 hover:text-rose-300 border border-white/[0.08] transition" title="Limpiar datos">Reset</button>
          )}
        </div>
      </div>

      {isDemo && (
        <div className="p-2.5 rounded-xl bg-amber-950/30 border border-amber-500/40 text-xs font-mono-tech text-amber-300 flex items-center justify-between gap-2">
          <span>ATENCION: MODO DEMO ACTIVO — Cifras ficticias para pruebas. Apaga el interruptor para ver datos reales.</span>
          <button type="button" onClick={() => setDemoMode(false)} className="px-2 py-0.5 rounded bg-amber-500 text-black font-bold text-[10px] uppercase">Apagar Demo</button>
        </div>
      )}

      {/* Honest Empty State Banner if no real data */}
      {!hasData && !isDemo && (
        <div className="bg-[#090b10] border border-amber-500/40 rounded-2xl p-4 sm:p-5 text-center space-y-3 shadow-xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-mono-tech font-bold uppercase tracking-wider">
            SIN DATOS REALES: 0 ventas, 0 impresiones registradas
          </div>
          <p className="text-xs sm:text-sm text-zinc-300 max-w-xl mx-auto leading-relaxed">
            Nada se ha publicado ni vendido todavia. No se muestran cifras inventadas. Importa tu reporte CSV de Gumroad o Hotmart, o registra metricas de publicaciones para alimentar el Radar.
          </p>
          <div className="flex justify-center gap-3 pt-1 flex-wrap">
            <button type="button" onClick={() => setShowModal(true)} className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-mono-tech font-bold text-xs uppercase tracking-wider transition shadow-lg">Importar CSV de Gumroad / Hotmart</button>
            <button type="button" onClick={() => setShowModal(true)} className="px-4 py-2 rounded-xl bg-white/[0.06] hover:bg-white/[0.1] text-zinc-200 border border-white/10 font-mono-tech text-xs uppercase tracking-wider transition">Registrar Metricas de Piezas</button>
          </div>
        </div>
      )}

      {(loadError || resetError) && (
        <div role="alert" className="p-2.5 rounded-xl bg-rose-950/40 border border-rose-500/40 text-[11px] text-rose-200 flex items-center justify-between gap-2">
          <span className="leading-relaxed break-words">{loadError ? `No se pudieron cargar las métricas: ${loadError}` : `No se pudo reiniciar: ${resetError}`}</span>
          <button type="button" onClick={() => void loadMetrics(demoMode)} className="shrink-0 px-2 py-0.5 rounded bg-rose-500/20 border border-rose-500/40 font-mono-tech font-bold">Reintentar</button>
        </div>
      )}

      {/* Mobile LAN Access Banner (sin IP inventada: si no hay lan_url, no se muestra dirección) */}
      <div className="bg-[#090b10] border border-emerald-500/25 rounded-2xl p-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
        <span className="flex items-center gap-2.5 text-zinc-300 font-mono-tech">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          {lanUrl ? <>Acceso LAN Wi-Fi Móvil: <code className="text-emerald-300 font-bold bg-black/60 px-1.5 py-0.5 rounded">{lanUrl}</code></> : 'LAN sin detectar: el backend no informó lan_url.'}
        </span>
        <button type="button" onClick={copyLan} disabled={!lanUrl} className="px-3 py-1 rounded-lg bg-emerald-500/15 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/30 font-mono-tech text-[11px] font-bold self-start sm:self-auto transition disabled:opacity-50">
          {copiedLan ? 'URL Copiada' : 'Copiar Link'}
        </button>
      </div>

      {/* Leading vs Lagging KPI Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div className="bg-[#090b10] border border-white/[0.08] rounded-2xl p-3.5">
          <div className="text-[10px] font-mono-tech uppercase text-zinc-400 tracking-wider">Leading • Impresiones</div>
          <div className="text-2xl sm:text-3xl font-extrabold text-white font-display tabular-nums mt-1">
            {hasData ? summary?.total_impressions.toLocaleString() : '0'}
          </div>
          <div className="text-[11px] text-emerald-400 font-mono-tech tabular-nums mt-1">
            CTR Saliente: {hasData && summary?.ctr_percent !== null ? `${summary?.ctr_percent}%` : '—'} ({hasData ? summary?.total_clicks : 0} clics)
          </div>
        </div>

        <div className="bg-[#090b10] border border-white/[0.08] rounded-2xl p-3.5">
          <div className="text-[10px] font-mono-tech uppercase text-zinc-400 tracking-wider">Leading • Saves Pinterest</div>
          <div className="text-2xl sm:text-3xl font-extrabold text-amber-400 font-display tabular-nums mt-1">
            {hasData ? `+${summary?.total_saves.toLocaleString()}` : '0'}
          </div>
          <div className="text-[11px] text-zinc-400 font-mono-tech tabular-nums mt-1">{products.length} rutas puente semánticas</div>
        </div>

        <div className="bg-[#090b10] border border-emerald-500/25 rounded-2xl p-3.5">
          <div className="text-[10px] font-mono-tech uppercase text-emerald-400 tracking-wider">Lagging • Ingresos Netos</div>
          <div className="text-2xl sm:text-3xl font-extrabold text-emerald-400 font-display tabular-nums mt-1">
            ${hasData ? (summary?.total_revenue_usd || 0).toFixed(2) : '0.00'} <span className="text-xs text-zinc-400 font-ui font-normal">USD</span>
          </div>
          <div className="text-[11px] text-zinc-300 font-mono-tech tabular-nums mt-1">
            Gumroad ${hasData ? (summary?.gumroad_revenue_usd || 0).toFixed(2) : '0.00'} • Hotmart ${hasData ? (summary?.hotmart_revenue_usd || 0).toFixed(2) : '0.00'}
          </div>
        </div>

        <div className="bg-[#090b10] border border-white/[0.08] rounded-2xl p-3.5">
          <div className="text-[10px] font-mono-tech uppercase text-zinc-400 tracking-wider">Lagging • AOV / RPM</div>
          <div className="text-2xl sm:text-3xl font-extrabold text-cyan-400 font-display tabular-nums mt-1">
            {hasData && summary?.aov_usd !== null ? `$${summary?.aov_usd} USD` : '—'}
          </div>
          <div className="text-[11px] text-amber-300 font-mono-tech tabular-nums mt-1">
            RPM: {hasData && summary?.rpm_usd !== null ? `$${summary?.rpm_usd}` : '—'} • {hasData ? summary?.total_sales : 0} ventas
          </div>
        </div>
      </div>

      {/* Regla de 14 Días: Doblar Ganadores vs Matar / Mutar Perdedores */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Columna Ganadores */}
        <div className="lg:col-span-7 bg-[#090b10] border border-white/[0.08] rounded-2xl p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-white/[0.07] pb-2.5">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 font-mono-tech">Ganadores (Criterio: Doblar Cadencia 2x)</span>
            <button onClick={() => onNavigateTab('bait_studio')} className="text-[11px] px-2.5 py-1 rounded-lg bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 font-mono-tech font-bold">+ Lab Anzuelos</button>
          </div>
          {summary?.winning_pieces && summary.winning_pieces.length > 0 ? (
            <div className="space-y-2">
              {summary.winning_pieces.map((p, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-black/60 border border-emerald-500/20 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 text-[10px] font-mono-tech text-emerald-400">
                      <span className="px-1.5 py-0.5 rounded bg-emerald-500/15 font-bold uppercase">DOBLAR #{idx + 1}</span>
                      <span>{p.platform.toUpperCase()}</span>
                      <span>• {p.piece_id}</span>
                      {p.sku_id && <span>• SKU {p.sku_id}</span>}
                    </div>
                    <p className="text-xs text-zinc-200 mt-1">{p.reason}</p>
                  </div>
                  <div className="flex items-center gap-3 shrink-0 font-mono-tech text-xs tabular-nums">
                    <span className="text-emerald-400 font-bold">{p.ctr_percent}% CTR</span>
                    <span className="text-zinc-400">{p.clicks} clics</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-6 rounded-xl bg-black/40 border border-white/[0.05] text-center text-xs text-zinc-500 font-mono-tech">
              {hasData ? 'No hay piezas con CTR >= 2.0% todavia.' : 'Sin datos suficientes para calcular ganadores.'}
            </div>
          )}
        </div>

        {/* Columna Criterio de Muerte */}
        <div className="lg:col-span-5 bg-[#090b10] border border-white/[0.08] rounded-2xl p-4 space-y-3 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center justify-between border-b border-white/[0.07] pb-2.5">
              <span className="text-xs font-bold uppercase tracking-wider text-rose-400 font-mono-tech">Criterio de Muerte 14D (Mutar o Purgar)</span>
              <span className="text-[10px] font-mono-tech font-bold px-2 py-0.5 rounded bg-rose-500/15 text-rose-300 border border-rose-500/30">Auto-Diagnóstico</span>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Regla del Grill: piezas con CTR &lt; 0.8% tras 48h deben mutar hook verbal o cambiar a Captura Anzuelo iOS 17.
            </p>
            {summary?.losing_pieces && summary.losing_pieces.length > 0 ? (
              <div className="space-y-2">
                {summary.losing_pieces.map((p, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-rose-950/20 border border-rose-500/30 space-y-1.5">
                    <div className="flex items-center justify-between text-[10px] font-mono-tech tabular-nums">
                      <span className="text-rose-300 font-bold uppercase">{p.verdict} • {p.piece_id}</span>
                      <span className="text-zinc-400">{p.ctr_percent}% CTR ({p.impressions} imp)</span>
                    </div>
                    <p className="text-xs text-zinc-300">{p.reason}</p>
                    <button type="button" onClick={() => onMutateHook(p.piece_id)} className="w-full py-1.5 px-3 rounded-lg bg-amber-500 hover:bg-amber-400 text-black font-bold text-xs font-mono-tech transition">
                      Mutar Gancho Verbal
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-4 rounded-xl bg-black/40 border border-white/[0.05] text-center text-xs text-zinc-500 font-mono-tech">
                {hasData ? 'Ninguna pieza en umbral de muerte actualmente.' : 'Sin datos suficientes para evaluar descarte.'}
              </div>
            )}
          </div>

          <div className="p-3 rounded-xl bg-black border border-white/[0.07] text-[11px] font-mono-tech text-zinc-400 space-y-1">
            <div className="text-emerald-400 font-bold">ESTADO DEL EMBUDO (55 SKUs):</div>
            <div>• Vía A (Ebooks/Apps): {summary?.funnel_breakdown?.via_a ?? 0}% de ventas</div>
            <div>• Vía B (Bóvedas/Arsenales): {summary?.funnel_breakdown?.via_b ?? 0}% de ventas</div>
            <div>• Vía C (Kits/Bundles/Lead): {summary?.funnel_breakdown?.via_c ?? 0}% de ventas</div>
          </div>
        </div>
      </div>

      <MetricsImportModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onRefresh={() => loadMetrics(demoMode)}
        availableSkus={products.map((p) => ({ sku_id: p.sku_id, title: p.title }))}
      />
    </div>
  );
};
