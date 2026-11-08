import React, { useEffect, useMemo, useState } from 'react';
import { generateSkuDeliverable } from '../../api/client';
import { copyText } from '../../utils/clipboard';
import type { ProductSKU } from '../../types/domain';
import { CoverArt } from './CoverArt';

export interface CatalogFactoryViewProps {
  products?: ProductSKU[];
  onToggleStan: (skuId: string) => Promise<unknown> | void;
}

const ELITE_SKUS = new Set(['A01', 'A02', 'A05', 'A08', 'A11', 'A12', 'E01', 'E02', 'E05', 'E08', 'B01', 'B05']);
const NICHE_GRADIENTS: Record<string, string> = {
  dinero_digital_faceless: 'from-emerald-950 via-[#0b0e14] to-black border-emerald-500/25',
  ia_automatizacion_injusta: 'from-cyan-950 via-[#0b0e14] to-black border-cyan-500/25',
  psicologia_oscura_persuasion: 'from-purple-950 via-[#0b0e14] to-black border-purple-500/25',
  escape_9a5_finanzas_cinicas: 'from-amber-950 via-[#0b0e14] to-black border-amber-500/25',
};
const FORMAT_BADGES: Record<string, string> = {
  micro_app_html: 'APP INTERACTIVA', ebook_blueprint: 'BLUEPRINT 8 CAPÍTULOS',
  boveda_arsenal: 'BÓVEDA BUSCABLE', kit_sistema: 'KIT SISTEMA',
  mega_bundle: 'MEGA BUNDLE', lead_magnet: 'LEAD MAGNET',
};

export const CatalogFactoryView: React.FC<CatalogFactoryViewProps> = ({ products = [], onToggleStan }) => {
  const [formatFilter, setFormatFilter] = useState('all');
  const [nicheFilter, setNicheFilter] = useState('all');
  const [flagshipOnly, setFlagshipOnly] = useState(false);
  const [search, setSearch] = useState('');
  const [togglingId, setTogglingId] = useState<string | null>(null);
  const [generatingSkuId, setGeneratingSkuId] = useState<string | null>(null);
  const [activeDeliverable, setActiveDeliverable] = useState<{ sku: ProductSKU; deliverableUrl: string } | null>(null);
  const [deliverableError, setDeliverableError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [copiedRoute, setCopiedRoute] = useState<string | null>(null);
  const [copyFailed, setCopyFailed] = useState(false);

  useEffect(() => {
    if (!activeDeliverable) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setActiveDeliverable(null);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [activeDeliverable]);

  const stats = useMemo(() => {
    const paid = products.filter((p) => p.price_usd > 0);
    const avg = paid.length ? paid.reduce((s, p) => s + p.price_usd, 0) / paid.length : 0;
    const routes = new Set(products.map((p) => p.bridge_route)).size;
    return { total: products.length, paid: paid.length, lead: products.length - paid.length, routes, avg };
  }, [products]);

  const filtered = useMemo(() => {
    return products.filter((p) => {
      if (flagshipOnly && !ELITE_SKUS.has(p.sku_id)) return false;
      if (formatFilter !== 'all' && p.format !== formatFilter) return false;
      if (nicheFilter !== 'all' && p.niche !== nicheFilter) return false;
      if (search) {
        const q = search.toLowerCase();
        return p.title.toLowerCase().includes(q) || p.sku_id.toLowerCase().includes(q) || p.hook_angle.toLowerCase().includes(q);
      }
      return true;
    });
  }, [products, flagshipOnly, formatFilter, nicheFilter, search]);

  const handleToggle = async (skuId: string) => {
    setTogglingId(skuId);
    setActionError(null);
    try { await onToggleStan(skuId); } catch (error) {
      setActionError(`No se pudo actualizar ${skuId} en Stan: ${error instanceof Error ? error.message : String(error)}`);
    } finally { setTogglingId(null); }
  };

  const handleOpenDeliverable = async (sku: ProductSKU) => {
    setGeneratingSkuId(sku.sku_id);
    setDeliverableError(null);
    try {
      const res = await generateSkuDeliverable(sku.sku_id);
      setActiveDeliverable({ sku, deliverableUrl: res.deliverable_url });
    } catch (error) {
      setDeliverableError(`No se pudo abrir el entregable ${sku.sku_id}: ${error instanceof Error ? error.message : String(error)}`);
    } finally { setGeneratingSkuId(null); }
  };

  const handleCopyRoute = (route: string) => {
    void copyText(route).then((ok) => {
      setCopyFailed(!ok);
      setCopiedRoute(ok ? route : null);
      window.setTimeout(() => setCopiedRoute(null), 1500);
    });
  };

  return (
    <div className="space-y-4 text-zinc-100 font-ui">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 pb-3 border-b border-white/[0.08]">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2 font-grotesque">
            <span className="p-1.5 bg-emerald-500/10 text-emerald-400 rounded-lg border border-emerald-500/20 text-xs font-mono-tech font-bold">ARSENAL</span>
            Catálogo Insider OS — 55 Entregables Comerciales
          </h1>
          <p className="text-xs text-zinc-400 mt-0.5">52 SKUs de pago + 3 lead magnets con arquitectura de 8 capítulos e inspector interactivo 82vh.</p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="bg-[#090b10] border border-white/[0.08] rounded-xl p-3">
          <span className="text-[10px] text-zinc-400 uppercase tracking-wider font-mono-tech font-bold">Total Catálogo</span>
          <div className="text-2xl font-black text-white font-display tabular-nums mt-0.5">{stats.total} <span className="text-xs text-zinc-500 font-normal font-ui">SKUs</span></div>
        </div>
        <div className="bg-[#090b10] border border-white/[0.08] rounded-xl p-3">
          <span className="text-[10px] text-zinc-400 uppercase tracking-wider font-mono-tech font-bold">SKUs de Pago</span>
          <div className="text-2xl font-black text-emerald-400 font-display tabular-nums mt-0.5">{stats.paid} <span className="text-xs text-zinc-500 font-normal font-ui">({stats.lead} free)</span></div>
        </div>
        <div className="bg-[#090b10] border border-white/[0.08] rounded-xl p-3">
          <span className="text-[10px] text-zinc-400 uppercase tracking-wider font-mono-tech font-bold">Rutas Puente</span>
          <div className="text-2xl font-black text-cyan-400 font-display tabular-nums mt-0.5">{stats.routes} <span className="text-xs text-zinc-500 font-normal font-ui">anti-spam</span></div>
        </div>
        <div className="bg-[#090b10] border border-white/[0.08] rounded-xl p-3">
          <span className="text-[10px] text-zinc-400 uppercase tracking-wider font-mono-tech font-bold">Precio Promedio</span>
          <div className="text-2xl font-black text-amber-400 font-display tabular-nums mt-0.5">${stats.avg.toFixed(1)} <span className="text-xs text-zinc-500 font-normal font-ui">USD</span></div>
        </div>
      </div>

      {(deliverableError || actionError || copyFailed) && (
        <div role="alert" className="p-2.5 rounded-xl bg-rose-950/40 border border-rose-500/40 text-[11px] text-rose-200 leading-relaxed">
          {deliverableError || actionError || 'No se pudo copiar la ruta al portapapeles (HTTP en LAN). Selecciona el texto manualmente.'}
        </div>
      )}

      <div className="flex flex-col md:flex-row gap-2 bg-[#090b10] p-3 rounded-xl border border-white/[0.08] text-xs items-center">
        <input aria-label="Buscar SKU por ID, título o gancho" type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Buscar ID (E01, B03...), título o gancho..." className="bg-black border border-zinc-800 rounded-lg px-2.5 py-1.5 text-xs text-zinc-200 flex-1 w-full font-ui" />
        <select aria-label="Filtrar por formato" value={formatFilter} onChange={(e) => setFormatFilter(e.target.value)} className="bg-black border border-zinc-800 rounded-lg px-2.5 py-1.5 text-zinc-300 font-ui">
          <option value="all">Todos los formatos</option><option value="ebook_blueprint">Ebook Blueprint</option>
          <option value="boveda_arsenal">Bóveda / Arsenal</option><option value="micro_app_html">Micro-App HTML</option>
          <option value="kit_sistema">Kit / Sistema</option><option value="mega_bundle">Mega Bundle</option><option value="lead_magnet">Lead Magnet (Gratis)</option>
        </select>
        <select aria-label="Filtrar por nicho" value={nicheFilter} onChange={(e) => setNicheFilter(e.target.value)} className="bg-black border border-zinc-800 rounded-lg px-2.5 py-1.5 text-zinc-300 font-ui">
          <option value="all">Todos los nichos</option><option value="dinero_digital_faceless">Dinero Digital Faceless</option>
          <option value="ia_automatizacion_injusta">IA & Automatización Injusta</option><option value="psicologia_oscura_persuasion">Psicología Oscura & Persuasión</option><option value="escape_9a5_finanzas_cinicas">Escape 9 a 5 & Finanzas</option>
        </select>
        <button type="button" onClick={() => setFlagshipOnly((b) => !b)} className={`px-3 py-1.5 rounded-lg font-mono-tech font-bold transition shrink-0 border ${flagshipOnly ? 'bg-amber-500/20 text-amber-300 border-amber-500/40 shadow' : 'bg-black text-zinc-400 border-zinc-800 hover:text-white'}`}>
          Edición Flagship (+100 KB)
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
        {filtered.map((sku) => {
          const isToggling = togglingId === sku.sku_id;
          const isGenerating = generatingSkuId === sku.sku_id;
          const isFree = sku.price_usd === 0;
          const isElite = ELITE_SKUS.has(sku.sku_id);
          const grad = NICHE_GRADIENTS[sku.niche] || 'from-zinc-900 to-black border-zinc-800';
          const formatBadge = FORMAT_BADGES[sku.format] || 'ENTREGABLE';

          return (
            <div key={sku.sku_id} className="bg-[#090b10] border border-white/[0.08] rounded-2xl overflow-hidden flex flex-col justify-between hover:border-emerald-500/40 transition shadow-lg">
              <div>
                <div className={`p-3.5 bg-gradient-to-br ${grad} border-b border-white/[0.06] relative flex gap-3`}>
                  <CoverArt skuId={sku.sku_id} title={sku.title} className="w-14 h-auto shrink-0 self-start" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-mono-tech px-2 py-0.5 bg-black/70 border border-white/10 text-emerald-400 font-bold rounded tabular-nums">{sku.sku_id}</span>
                      <span className="text-[9px] font-mono-tech px-2 py-0.5 bg-black/60 text-zinc-300 rounded border border-white/5">{formatBadge}</span>
                    </div>
                    <h3 className="text-xs font-bold text-white mt-1.5 leading-snug line-clamp-1 font-ui">{sku.title}</h3>
                    <div className="mt-2 flex items-baseline justify-between font-mono-tech">
                      {isFree ? (
                        <span className="text-xs font-bold text-cyan-400">GRATIS (Lead Magnet)</span>
                      ) : (
                        <div className="flex items-baseline gap-1.5">
                          <span className="text-sm font-black text-emerald-400 font-display tabular-nums">${sku.price_usd} USD</span>
                          <span className="text-[10px] text-zinc-400 font-mono-tech tabular-nums">(${sku.price_cop.toLocaleString('es-CO')} COP)</span>
                        </div>
                      )}
                      {isElite && <span className="text-[9px] font-bold text-amber-300 bg-amber-500/20 px-1.5 py-0.5 rounded border border-amber-500/30">FLAGSHIP</span>}
                    </div>
                  </div>
                </div>

                <div className="p-3.5 space-y-2.5">
                  <p className="text-[11px] text-zinc-400 line-clamp-2 leading-relaxed">{sku.subtitle}</p>
                  <div className="pt-2 border-t border-white/[0.05] space-y-1.5 text-[10px]">
                    <div className="flex items-center justify-between">
                      <span className="font-mono-tech text-zinc-500">Ruta:</span>
                      <button type="button" onClick={() => handleCopyRoute(sku.bridge_route)} className="text-cyan-400 bg-black px-1.5 py-0.5 rounded border border-cyan-500/30 hover:border-cyan-400 font-mono-tech text-[9px] truncate max-w-[170px] transition inline-flex items-center gap-1">
                        {copiedRoute === sku.bridge_route && <svg className="w-2.5 h-2.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={3} aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7" strokeLinecap="round" strokeLinejoin="round" /></svg>}
                        {copiedRoute === sku.bridge_route ? 'Copiado' : sku.bridge_route}
                      </button>
                    </div>
                    <div className="text-zinc-400 truncate"><span className="font-mono-tech text-zinc-500">Gancho: </span><span className="text-zinc-300 italic">{sku.hook_angle}</span></div>
                  </div>
                </div>
              </div>

              <div className="p-3.5 pt-0 flex gap-2">
                <button disabled={isGenerating} onClick={() => handleOpenDeliverable(sku)} className="flex-1 py-1.5 px-2 rounded-xl text-[11px] font-bold bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 transition flex items-center justify-center gap-1 shadow font-mono-tech">
                  {isGenerating ? 'Abriendo...' : 'Probar .HTML'}
                </button>
                <button disabled={isToggling} onClick={() => handleToggle(sku.sku_id)} className={`px-2.5 py-1.5 rounded-xl text-[10px] font-mono-tech font-medium border transition ${sku.featured_on_stan ? 'bg-amber-500/15 text-amber-300 border-amber-500/30' : 'bg-black text-zinc-400 border-zinc-800'}`}>
                  {isToggling ? '...' : sku.featured_on_stan ? 'En Stan' : '+ Stan'}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {activeDeliverable && (
        <div className="fixed inset-0 z-50 bg-black/90 backdrop-blur-md flex items-center justify-center p-3 font-ui">
          <div role="dialog" aria-modal="true" aria-label={`Entregable ${activeDeliverable.sku.sku_id}`} className="w-full max-w-6xl bg-[#090b10] border border-zinc-700/80 rounded-2xl p-4 shadow-2xl flex flex-col gap-2.5">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-zinc-800 pb-2.5">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono-tech font-bold px-2 py-0.5 bg-emerald-500/20 text-emerald-300 rounded border border-emerald-500/40 tabular-nums">{activeDeliverable.sku.sku_id}</span>
                <select aria-label="Cambiar entregable" value={activeDeliverable.sku.sku_id} onChange={(e) => { const next = products.find((p) => p.sku_id === e.target.value); if (next) void handleOpenDeliverable(next); }} className="bg-black border border-zinc-700 rounded px-2 py-1 text-xs text-white max-w-xs font-semibold">
                  {products.map((p) => (<option key={p.sku_id} value={p.sku_id}>{p.sku_id} — {p.title}</option>))}
                </select>
                <span className="text-xs text-emerald-400 font-mono-tech font-semibold tabular-nums">${activeDeliverable.sku.price_usd} USD</span>
              </div>
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-[11px] px-2.5 py-1 bg-amber-500/15 border border-amber-500/40 text-amber-300 rounded-lg font-mono-tech">Order Bump: +$9 USD</span>
                <button type="button" onClick={() => window.open(activeDeliverable.deliverableUrl, '_blank')} className="text-xs font-mono-tech font-bold px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg transition inline-flex items-center gap-1.5">
                  <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.2} aria-hidden="true"><path d="M4.5 19.5l15-15m0 0H8.25m11.25 0v11.25" strokeLinecap="round" strokeLinejoin="round" /></svg>
                  Pestaña completa
                </button>
                <button type="button" onClick={() => setActiveDeliverable(null)} aria-label="Cerrar visor" className="text-xs font-mono-tech px-2.5 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded-lg inline-flex items-center gap-1.5">
                  <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.2} aria-hidden="true"><path d="M6 6l12 12M18 6 6 18" strokeLinecap="round" /></svg>
                  Cerrar
                </button>
              </div>
            </div>
            <iframe src={activeDeliverable.deliverableUrl} title={activeDeliverable.sku.title} className="w-full h-[82vh] rounded-xl border border-zinc-800 bg-black" />
          </div>
        </div>
      )}
    </div>
  );
};
