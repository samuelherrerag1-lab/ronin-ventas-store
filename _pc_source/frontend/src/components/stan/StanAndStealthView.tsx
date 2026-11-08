import React, { useMemo, useState } from 'react';
import type { CompetitorTeardown, ProductSKU, StealthDiagnostic } from '../../types/domain';
import { copyText } from '../../utils/clipboard';
import { StealthForensicsPanel } from './StealthForensicsPanel';

export interface StanAndStealthViewProps {
  products?: ProductSKU[];
  stealthDiagnostic?: StealthDiagnostic;
  competitorTeardowns?: CompetitorTeardown[];
}

const VerifiedBadge = () => (
  <svg className="w-3.5 h-3.5 text-[#0095F6] inline ml-1 fill-current shrink-0" viewBox="0 0 24 24" aria-hidden="true">
    <path d="M10.067.87a2.89 2.89 0 0 1 3.866 0l1.197 1.054a2.89 2.89 0 0 0 2.219.72l1.58-.152a2.89 2.89 0 0 1 3.128 2.272l.37 1.547a2.89 2.89 0 0 0 1.42 1.867l1.378.783a2.89 2.89 0 0 1 1.434 3.593l-.565 1.49a2.89 2.89 0 0 0 0 2.348l.565 1.49a2.89 2.89 0 0 1-1.434 3.593l-1.378.783a2.89 2.89 0 0 0-1.42 1.867l-.37 1.547a2.89 2.89 0 0 1-3.128 2.272l-1.58-.152a2.89 2.89 0 0 0-2.219-.72l-1.197 1.054a2.89 2.89 0 0 1-3.866 0l-1.197-1.054a2.89 2.89 0 0 0-2.219-.72l-1.58.152a2.89 2.89 0 0 1-3.128-2.272l-.37-1.547a2.89 2.89 0 0 0-1.42-1.867l-1.378-.783a2.89 2.89 0 0 1-1.434-3.593l.565-1.49a2.89 2.89 0 0 0 0-2.348l-.565-1.49a2.89 2.89 0 0 1 1.434-3.593l1.378-.783a2.89 2.89 0 0 0 1.42-1.867l.37-1.547a2.89 2.89 0 0 1 3.128-2.272l1.58.152a2.89 2.89 0 0 0 2.219-.72l1.197-1.054ZM16.67 8.27l-5.656 5.657-2.828-2.829-1.414 1.415 4.242 4.242 7.07-7.07-1.414-1.415Z" />
  </svg>
);

const ArrowIcon = () => (
  <svg className="w-3 h-3 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.2} aria-hidden="true">
    <path d="M5 12h14m0 0-5-5m5 5-5 5" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

export const StanAndStealthView: React.FC<StanAndStealthViewProps> = ({
  products = [], stealthDiagnostic, competitorTeardowns = [],
}) => {
  const [subView, setSubView] = useState<'stan' | 'stealth'>('stan');
  const [withOrderBump, setWithOrderBump] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [selectedSkuId, setSelectedSkuId] = useState<string | null>(null);

  const paidProducts = useMemo(() => products.filter((p) => p.price_usd > 0), [products]);
  const selectedSku = paidProducts.find((p) => p.sku_id === selectedSkuId) ?? paidProducts[0] ?? null;
  const baseUsd = selectedSku?.price_usd ?? 0;
  const baseCop = selectedSku?.price_cop ?? 0;
  const totalUsd = withOrderBump ? baseUsd + 9 : baseUsd;
  const totalCop = withOrderBump ? baseCop + 37800 : baseCop;
  const checkoutUrl = selectedSku?.gumroad_url || selectedSku?.hotmart_url || '';

  const handleCheckoutClick = (gateway: 'hotmart' | 'gumroad') => {
    const url = gateway === 'hotmart' ? selectedSku?.hotmart_url : selectedSku?.gumroad_url;
    if (!url) {
      setNotice(`Sin checkout de ${gateway} para ${selectedSku?.sku_id ?? 'este SKU'}. Configúralo en Publicar > Checkout.`);
      return;
    }
    window.open(url, '_blank', 'noopener');
  };

  const handleCopyFormula = (comp: CompetitorTeardown) => {
    void copyText(`Competidor: ${comp.handle}\nCadencia: ${comp.cadence}\nMecanismo: ${comp.real_mechanism}\nRobamos: ${comp.what_we_steal}`).then((ok) => {
      setNotice(ok ? `Fórmula de ${comp.handle} copiada al portapapeles` : 'No se pudo copiar al portapapeles.');
      window.setTimeout(() => setNotice(null), 3000);
    });
  };

  return (
    <div className="space-y-4 text-zinc-100 font-ui">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3 border-b border-white/[0.08]">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2 font-grotesque">
            <span className="p-1.5 bg-[#E07A5F]/15 text-[#E07A5F] rounded-lg border border-[#E07A5F]/30 text-xs font-mono-tech font-bold">STAN PRO</span>
            Stan Store Pro Mobile & Expedientes Forenses Stealth
          </h1>
          <p className="text-xs text-zinc-400 mt-0.5">Storefront móvil 1:1, embudo de 5 bloques con Order Bump y telemetría liarjs anti-bot.</p>
        </div>
        <div className="flex items-center gap-1 bg-[#090b10] p-1 rounded-xl border border-white/[0.08] text-xs font-mono-tech">
          <button type="button" onClick={() => setSubView('stan')} className={`px-2.5 sm:px-3 py-1.5 rounded-lg text-[11px] sm:text-xs font-medium transition ${subView === 'stan' ? 'bg-zinc-800 text-[#E07A5F] shadow-sm font-bold' : 'text-zinc-400 hover:text-zinc-200'}`}>Stan Store & Mini-Landing</button>
          <button type="button" onClick={() => setSubView('stealth')} className={`px-2.5 sm:px-3 py-1.5 rounded-lg text-[11px] sm:text-xs font-medium transition ${subView === 'stealth' ? 'bg-zinc-800 text-emerald-400 shadow-sm font-bold' : 'text-zinc-400 hover:text-zinc-200'}`}>Expedientes Stealth & Teardowns</button>
        </div>
      </div>

      {notice && <div role="status" className="p-2.5 bg-[#090b10] border border-emerald-500/40 rounded-xl text-xs text-emerald-300 font-mono-tech flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />{notice}</div>}

      {subView === 'stan' && (
        paidProducts.length === 0 ? (
          <div className="p-6 rounded-2xl bg-[#090b10] border border-white/[0.08] text-center space-y-2">
            <p className="text-sm text-zinc-200 font-semibold">No hay SKUs de pago cargados.</p>
            <p className="text-xs text-zinc-400 max-w-xl mx-auto leading-relaxed">
              Esta vista usa el catálogo real del backend. Si el catálogo no responde, no se muestran productos inventados.
              Revisa el Sync OS o la pestaña Fábrica 55 Productos.
            </p>
          </div>
        ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
          {/* Captura / Interfaz Web Móvil 1:1 de Stan Store Pro Dark */}
          <div className="lg:col-span-5 flex justify-center">
            <div className="w-full max-w-[360px] rounded-[28px] bg-[#0c0e14] border border-white/10 shadow-2xl overflow-hidden select-none flex flex-col">
              <div className="bg-[#12151d] px-3 py-2 border-b border-white/10 flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-rose-500/80" />
                  <span className="w-2 h-2 rounded-full bg-amber-500/80" />
                  <span className="w-2 h-2 rounded-full bg-emerald-500/80" />
                </div>
                <span className="text-[10px] font-mono-tech font-bold px-2 py-0.5 bg-black/80 text-emerald-400 rounded-full border border-emerald-500/30">stan.store/ronoverthinks</span>
                <span className="text-[8px] font-mono-tech text-zinc-500 uppercase">PRO</span>
              </div>
              <div className="h-14 bg-gradient-to-r from-zinc-900 via-zinc-800 to-black border-b border-white/5 relative" />
              <div className="px-4 pb-3 pt-0 text-center space-y-1.5 relative">
                <div className="-mt-7 mx-auto w-14 h-14 rounded-full overflow-hidden ring-2 ring-[#E07A5F] shadow-xl bg-black relative z-10">
                  <img src="/generated_images/ron_avatar_profile.png" alt="@ronoverthinks" className="w-full h-full object-cover" />
                </div>
                <h2 className="text-sm font-bold text-white tracking-tight flex items-center justify-center font-grotesque">@ronoverthinks <VerifiedBadge /></h2>
                <p className="text-[11px] text-zinc-300 leading-snug px-1">Sistemas de ingresos digitales faceless. 0 postureo, 100% código y apalancamiento.</p>
                <div className="flex justify-center gap-2 pt-1 text-[10px] text-zinc-400 font-mono-tech">
                  <span className="px-2 py-0.5 bg-white/5 rounded-full border border-white/5">Threads</span>
                  <span className="px-2 py-0.5 bg-white/5 rounded-full border border-white/5">Pinterest</span>
                  <span className="px-2 py-0.5 bg-white/5 rounded-full border border-white/5">Gumroad</span>
                </div>
              </div>

              <div className="px-3 pb-4 space-y-2.5 max-h-[440px] overflow-y-auto">
                <div className="text-center py-1 px-2 rounded-lg bg-white/[0.03] border border-white/[0.06] text-[9px] font-mono-tech text-zinc-400 uppercase tracking-wider">
                  Catálogo real — {paidProducts.length} SKUs de pago
                </div>
                {paidProducts.map((p) => {
                  const isSelected = selectedSku?.sku_id === p.sku_id;
                  return (
                    <div key={p.sku_id} onClick={() => setSelectedSkuId(p.sku_id)} className={`cursor-pointer rounded-2xl bg-[#12151d] border p-3 transition flex flex-col justify-between ${isSelected ? 'border-[#E07A5F] ring-1 ring-[#E07A5F]/40 shadow-xl' : 'border-white/10 hover:border-white/20'}`}>
                      <div className="flex items-start gap-3">
                        <div className="w-12 h-12 shrink-0 rounded-xl bg-black border border-white/10 flex items-center justify-center text-white font-mono-tech font-bold text-xs shadow-md">{p.sku_id}</div>
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center justify-between text-[10px]">
                            <span className="text-zinc-400 font-mono-tech text-[10px]">{p.format ? p.format.replace('_', ' ') : 'PRODUCTO'}</span>
                            <span className="text-zinc-500 font-mono-tech">{p.sku_id}</span>
                          </div>
                          <h4 className="text-xs font-bold text-white truncate leading-snug mt-0.5 font-ui">{p.title}</h4>
                          <p className="text-[10px] text-zinc-400 line-clamp-1 mt-0.5">{p.subtitle}</p>
                          <div className="mt-1 flex items-baseline gap-1.5 font-mono-tech">
                            <span className="text-xs font-black text-emerald-400 font-display tabular-nums">${p.price_usd} USD</span>
                            <span className="text-[10px] text-zinc-500 tabular-nums">(${p.price_cop.toLocaleString('es-CO')} COP)</span>
                          </div>
                        </div>
                      </div>
                      <button type="button" onClick={(e) => { e.stopPropagation(); setSelectedSkuId(p.sku_id); }} className="w-full mt-2 py-1.5 rounded-xl bg-white hover:bg-zinc-200 text-black font-mono-tech font-bold text-[11px] uppercase tracking-wider transition text-center shadow inline-flex items-center justify-center gap-1.5">
                        Obtener acceso <ArrowIcon />
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Columna Derecha: Estructura de Conversión de 5 Bloques */}
          <div className="lg:col-span-7 bg-[#090b10] border border-white/[0.08] rounded-2xl p-4 space-y-3">
            {selectedSku ? (
              <div className="space-y-3">
                <div className="border-b border-white/[0.08] pb-3 flex items-start justify-between gap-3">
                  <div>
                    <span className="text-[10px] font-mono-tech px-2 py-0.5 rounded bg-purple-500/15 text-purple-300 border border-purple-500/30">Ruta Puente: {selectedSku.bridge_route}</span>
                    <h2 className="text-base font-black text-white mt-1.5 font-grotesque">{selectedSku.title}</h2>
                    <p className="text-xs text-zinc-300 mt-0.5">{selectedSku.subtitle}</p>
                  </div>
                  <a href={selectedSku.bridge_route} target="_blank" rel="noreferrer" className="text-xs px-2.5 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-emerald-400 border border-emerald-500/30 font-mono-tech font-semibold transition shrink-0 flex items-center gap-1.5" title="Ruta puente (requiere el sitio estático exportado)">
                    <ArrowIcon />
                    <span>Ver ruta puente</span>
                  </a>
                </div>

                <div className="p-3 bg-black/60 rounded-xl border border-white/[0.06] flex items-center justify-between text-xs font-mono-tech">
                  <div><span className="text-[10px] text-zinc-500 block uppercase font-bold">Muestra visual (simulación)</span><span className="text-emerald-400 font-bold font-display tabular-nums">$418.50 USD</span> <span className="text-zinc-400 text-[11px]">(Notificación iOS 3:14 AM)</span></div>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">Sin Rostro</span>
                </div>

                <div className="p-3 bg-black/40 rounded-xl border border-white/[0.06] text-xs space-y-1">
                  <div className="text-[10px] font-mono-tech text-zinc-400 uppercase font-bold">Qué Incluye la Arquitectura:</div>
                  <ul className="text-zinc-300 text-[11px] space-y-1 list-disc list-inside">
                    <li>Sistema Offline de 8 Capítulos con Filosofía de Asimetría</li>
                    <li>Bóveda de 15 Hooks y Scripts Cínicos Copiables en 1 Clic</li>
                    <li>Simulador de ROI Diario y Checklist de 14 Días persistente</li>
                  </ul>
                </div>

                <div className="border-2 border-dashed border-amber-400/80 bg-amber-500/10 rounded-xl p-3.5 space-y-1.5">
                  <label className="flex items-start gap-2.5 cursor-pointer">
                    <input type="checkbox" checked={withOrderBump} onChange={(e) => setWithOrderBump(e.target.checked)} className="mt-0.5 w-4 h-4 rounded border-amber-400 text-amber-500 focus:ring-amber-400" />
                    <div className="text-xs">
                      <span className="font-bold text-amber-300 font-ui">Sí, agregar la Bóveda de 500 Hooks Cínicos + Calculadora por solo +$9 USD (75% DTO)</span>
                      <p className="text-[11px] text-zinc-300 mt-0.5">Multiplica tus conversiones en Threads con hooks virales probados y calculadora ROI en 1 clic.</p>
                    </div>
                  </label>
                </div>

                <div className="space-y-2 pt-1 font-mono-tech">
                  <button type="button" onClick={() => handleCheckoutClick('hotmart')} className="w-full py-2.5 px-3 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-400 text-zinc-950 transition flex items-center justify-center gap-1.5 shadow disabled:opacity-60" disabled={!selectedSku.hotmart_url} title={selectedSku.hotmart_url ? 'Abrir checkout Hotmart' : 'Sin checkout Hotmart configurado. Configúralo en Publicar > Checkout.'}>
                    <svg className="w-3.5 h-3.5 fill-current shrink-0" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2C9.5 6 7 9 7 13a5 5 0 0010 0c0-1.5-.5-3-1.5-4.5C14.5 10 13 11.5 13 13a1 1 0 11-2 0c0-2.5 2-4.5 3-6-1 0-2.5 1-3.5 2.5C10 8 11 5 12 2z" /></svg>
                    <span>Pagar con Nequi / PSE / Efecty (Hotmart — ${totalCop.toLocaleString('es-CO')} COP)</span>
                  </button>
                  <button type="button" onClick={() => handleCheckoutClick('gumroad')} className="w-full py-2.5 px-3 rounded-xl text-xs font-bold bg-[#FF90E8] hover:bg-[#ff7ae5] text-black transition flex items-center justify-center gap-1.5 shadow disabled:opacity-60" disabled={!selectedSku.gumroad_url} title={selectedSku.gumroad_url ? 'Abrir checkout Gumroad' : 'Sin checkout Gumroad configurado. Configúralo en Publicar > Checkout.'}>
                    <span className="w-4 h-4 rounded-full bg-black text-[#FF90E8] font-black text-[11px] flex items-center justify-center shrink-0">G</span>
                    <span>Pago Rápido Internacional USD (Gumroad Apple Pay — ${totalUsd} USD)</span>
                  </button>
                  {!checkoutUrl && (
                    <p className="text-[10px] text-amber-300/90 leading-relaxed">
                      Este SKU no tiene checkout configurado. Ve a Publicar &gt; Checkout por SKU para guardar las URLs de Gumroad/Hotmart.
                    </p>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-zinc-500"><p className="text-xs">Selecciona un producto en el móvil para ver su embudo de conversión.</p></div>
            )}
          </div>
        </div>
        )
      )}

      {subView === 'stealth' && (
        <div className="space-y-4">
          <StealthForensicsPanel diagnostic={stealthDiagnostic} />

          <div className="space-y-2.5">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-[#E07A5F] font-mono-tech">Ingeniería Inversa de Cuentas Competidoras</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {competitorTeardowns.map((comp) => (
                <div key={comp.handle} className="bg-[#090b10] border border-white/[0.08] rounded-xl p-3.5 space-y-2 flex flex-col justify-between">
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-white font-grotesque">{comp.handle}</span>
                      <span className="text-[9px] px-1.5 py-0.5 bg-black border border-zinc-800 text-zinc-400 rounded font-mono-tech tabular-nums">{comp.followers.toLocaleString()} fans</span>
                    </div>
                    <div className="text-[10px] text-zinc-400 font-mono-tech">{comp.platform} · {comp.cadence}</div>
                    <div className="text-[10px] text-zinc-300 bg-black/60 p-2 rounded border border-white/[0.05] leading-relaxed"><span className="text-zinc-500 font-semibold block text-[9px] font-mono-tech">Mecanismo Real:</span>{comp.real_mechanism}</div>
                    <div className="text-[10px] text-amber-300 bg-amber-950/20 p-2 rounded border border-amber-800/30 leading-relaxed"><span className="text-amber-500 font-semibold block text-[9px] font-mono-tech">Lo que robamos:</span>{comp.what_we_steal}</div>
                  </div>
                  <button type="button" onClick={() => handleCopyFormula(comp)} className="w-full mt-2 py-1 px-2 bg-zinc-800 hover:bg-zinc-700 text-emerald-300 border border-emerald-500/30 rounded-lg text-[10px] font-mono-tech font-bold transition">
                    Copiar Fórmula al Lab
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
