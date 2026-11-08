import React, { useEffect, useState } from 'react';
import type { PinterestPinItem } from '../../types/domain';
import { copyText } from '../../utils/clipboard';
import { PinPosterCanvas } from './PinPosterCanvas';

interface Props {
  pins: PinterestPinItem[];
  includeBenchmarks: boolean;
  onToggleBenchmarks: () => void;
  onToggleStatus: (pinId: string) => void;
  loading?: boolean;
}

const LANES = [
  { id: 'all', label: 'Todos' },
  { id: 'dinero_ia_directo', label: 'Dinero/IA Directo' },
  { id: 'caballo_de_troya_curiosidad', label: 'Caballo de Troya' },
  { id: 'demo_herramienta_html', label: 'Demo Micro-App HTML' },
];

const PinterestLogo = () => (
  <svg className="w-8 h-8 fill-[#E60023] shrink-0" viewBox="0 0 24 24"><path d="M12 0a12 12 0 0 0-4.37 23.18c-.06-.94-.12-2.39.02-3.42l1-4.25s-.26-.52-.26-1.28c0-1.2.7-2.1 1.57-2.1.74 0 1.1.56 1.1 1.22 0 .74-.47 1.86-.72 2.89-.2.87.43 1.57 1.28 1.57 1.54 0 2.73-1.63 2.73-3.97 0-2.08-1.49-3.53-3.63-3.53-2.65 0-4.2 1.99-4.2 4.04 0 .8.31 1.66.7 2.13.08.1.09.18.06.3l-.27 1.1c-.04.18-.15.22-.35.13-1.3-.6-2.11-2.5-2.11-4.02 0-3.27 2.38-6.28 6.87-6.28 3.6 0 6.4 2.57 6.4 6 0 3.58-2.26 6.46-5.4 6.46-1.05 0-2.04-.55-2.38-1.2l-.65 2.47c-.24.91-.88 2.05-1.31 2.75A12 12 0 1 0 12 0z" /></svg>
);

const ExternalArrow = () => (
  <svg className="w-3 h-3 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5}><path strokeLinecap="round" strokeLinejoin="round" d="M4.5 19.5l15-15m0 0H8.25m11.25 0v11.25" /></svg>
);

const ShareIcon = () => (
  <svg className="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24"><path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92 1.61 0 2.92-1.31 2.92-2.92s-1.31-2.92-2.92-2.92z" /></svg>
);

const EyeMark = () => (
  <svg className="w-3.5 h-3.5 fill-none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
);

export const PinterestCloneView: React.FC<Props> = ({ pins, includeBenchmarks, onToggleBenchmarks, onToggleStatus, loading }) => {
  const [lane, setLane] = useState('all');
  const [activePin, setActivePin] = useState<PinterestPinItem | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [copyFailed, setCopyFailed] = useState(false);

  const filtered = pins.filter((p) => {
    if (!includeBenchmarks && p.is_competitor_benchmark) return false;
    if (lane !== 'all' && p.strategy_lane !== lane) return false;
    return true;
  });

  const copy = (key: string, text: string) => {
    void copyText(text).then((ok) => {
      setCopyFailed(!ok);
      setCopiedId(ok ? key : null);
      window.setTimeout(() => setCopiedId(null), 1600);
    });
  };

  const ronCount = filtered.filter((p) => !p.is_competitor_benchmark).length;
  const compCount = filtered.filter((p) => p.is_competitor_benchmark).length;

  useEffect(() => {
    if (!activePin) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setActivePin(null);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [activePin]);

  return (
    <div className="max-w-[1560px] mx-auto py-5 px-3 sm:px-6 text-zinc-100 font-[-apple-system,BlinkMacSystemFont,'Segoe_UI',Roboto,Helvetica,Arial,sans-serif]">
      <div className="mb-6 pb-4 border-b border-zinc-800">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <div className="flex items-center gap-3">
            <PinterestLogo />
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold tracking-tight text-white font-grotesque">Pinterest Feed</span>
                <span className="px-2 py-0.5 text-xs rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/40 font-mono-tech font-bold">6 Arquetipos 2:3</span>
              </div>
              <p className="text-xs text-zinc-400 mt-0.5 font-ui">Pósters editoriales de alto impacto y puentes silenciosos de conversión</p>
            </div>
          </div>
          <button onClick={onToggleBenchmarks} className={`px-3.5 py-1.5 text-xs rounded-full font-medium border flex items-center gap-2 transition ${includeBenchmarks ? 'bg-rose-950/80 border-rose-500 text-rose-200 shadow-lg shadow-rose-950/40' : 'bg-zinc-900 border-zinc-700 text-zinc-400 hover:bg-zinc-800'}`}>
            <EyeMark /><span>{includeBenchmarks ? 'Modo Infiltración ACTIVO' : 'Modo Infiltración OFF'}</span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-black/50 font-mono-tech">{compCount} Competidores</span>
          </button>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-2.5 text-xs">
          <div className="flex flex-wrap gap-1.5">
            {LANES.map((t) => (
              <button key={t.id} onClick={() => setLane(t.id)} className={`px-3.5 py-1.5 rounded-full transition font-medium ${lane === t.id ? 'bg-white text-black font-semibold shadow' : 'bg-zinc-900 text-zinc-400 hover:bg-zinc-800'}`}>
                {t.label}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-3 text-zinc-400 font-mono-tech text-[11px] tabular-nums">
            <span>Ron: <b className="text-emerald-400">{ronCount}</b></span>
            <span>Bench: <b className="text-rose-400">{compCount}</b></span>
            <span className="px-2 py-0.5 rounded bg-white/[0.04] text-[9px] text-zinc-500 border border-white/[0.06]">VISTA PREVIA — cifras de ejemplo</span>
          </div>
        </div>
      </div>

      {loading && <div className="text-center py-8 text-zinc-500 animate-pulse text-xs font-mono-tech">Cargando tablero Pinterest...</div>}
      {copyFailed && (
        <div role="alert" className="mb-3 p-2 rounded-lg bg-rose-950/50 border border-rose-500/40 text-[11px] text-rose-200">
          No se pudo copiar al portapapeles (HTTP en LAN bloquea navigator.clipboard). Selecciona el texto y copia manualmente.
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        {filtered.map((pin, idx) => {
          const isComp = pin.is_competitor_benchmark;
          return (
            <div key={pin.pin_id} className="group relative flex flex-col justify-between">
              <div onClick={() => setActivePin(pin)} className="rounded-[16px] overflow-hidden relative group cursor-zoom-in aspect-[2/3] bg-zinc-900 shadow-lg border border-zinc-800/80">
                <PinPosterCanvas pin={pin} index={idx} />
                <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-150 bg-black/45 inset-0 absolute p-3 flex flex-col justify-between z-20">
                  <div className="flex items-center justify-between gap-1">
                    <div className="text-white text-xs font-semibold px-2 py-1.5 bg-black/40 backdrop-blur rounded-full flex items-center gap-1">
                      <span className="truncate max-w-[100px]">{pin.board_name || 'Ingresos'}</span>
                      <svg className="w-3 h-3 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.2} aria-hidden="true"><path d="m6 9 6 6 6-6" strokeLinecap="round" strokeLinejoin="round" /></svg>
                    </div>
                    <button type="button" aria-label={`Guardar seguimiento local de ${pin.seo_title}`} title="Seguimiento local: no guarda en Pinterest" onClick={(e) => { e.stopPropagation(); onToggleStatus(pin.pin_id); }} className="bg-[#E60023] hover:bg-[#ad081b] text-white font-semibold text-xs px-4 py-2.5 rounded-full shadow-md transition">Guardar</button>
                  </div>
                  <div className="flex items-center justify-between gap-1.5">
                    <div onClick={(e) => { e.stopPropagation(); copy(pin.pin_id, pin.bridge_route); }} className="bg-white/90 hover:bg-white text-black text-[11px] font-semibold px-3 py-1.5 rounded-full flex items-center gap-1 truncate max-w-[65%] shadow cursor-pointer transition">
                      <ExternalArrow /><span className="truncate">{pin.bridge_route.replace(/^\//, '')}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <button type="button" aria-label={`Copiar metadatos de ${pin.seo_title}`} title="Copiar título y ruta" onClick={(e) => { e.stopPropagation(); copy(`share-${pin.pin_id}`, `${pin.seo_title}\n${pin.bridge_route}`); }} className="w-8 h-8 rounded-full bg-white/90 hover:bg-white text-black flex items-center justify-center shrink-0 shadow transition"><ShareIcon /></button>
                      <button type="button" aria-label={`Ver detalles de ${pin.seo_title}`} onClick={(e) => { e.stopPropagation(); setActivePin(pin); }} className="w-8 h-8 rounded-full bg-white/90 hover:bg-white text-black flex items-center justify-center shrink-0 shadow transition">
                        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><circle cx="5" cy="12" r="1.7" /><circle cx="12" cy="12" r="1.7" /><circle cx="19" cy="12" r="1.7" /></svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-2 space-y-1.5 text-xs">
                <div onClick={() => setActivePin(pin)} className="font-semibold text-zinc-100 hover:underline line-clamp-2 cursor-pointer leading-snug text-[13px]">{pin.seo_title}</div>
                <div className="flex items-center justify-between text-[11px] text-zinc-400">
                  <div className="flex items-center gap-1.5 truncate pr-1">
                    <div className="w-5 h-5 rounded-full overflow-hidden shrink-0 border border-zinc-700 bg-black flex items-center justify-center">
                      {isComp ? <span className="text-[10px] font-bold text-white font-mono-tech">C</span> : <img src="/generated_images/ron_avatar_profile.png" alt="Ron" className="w-full h-full object-cover" />}
                    </div>
                    <span className="truncate text-zinc-300">{isComp ? (pin.competitor_source || '@competitor') : '@ronoverthinks'}</span>
                  </div>
                  <div className="flex items-center gap-1.5 shrink-0 font-mono-tech text-[10px] tabular-nums" title="VISTA PREVIA — cifras de ejemplo">
                    <span className="text-[8px] text-zinc-500 bg-white/5 px-1 rounded">EJEMPLO</span>
                    <span className="flex items-center gap-0.5"><svg className="w-3 h-3 fill-rose-500 shrink-0" viewBox="0 0 24 24"><path d="M16 12V4h1V2H7v2h1v8l-2 2v2h5.2v6l.8.8.8-.8v-6H18v-2l-2-2z" /></svg>{pin.simulated_saves}</span>
                    <span className="text-zinc-500 flex items-center gap-0.5"><EyeMark />{pin.simulated_outbound_clicks}</span>
                  </div>
                </div>
                <div className="flex items-center justify-between gap-1 pt-1.5 border-t border-zinc-800/80 font-mono-tech">
                  <button onClick={() => setActivePin(pin)} className="px-2 py-0.5 text-[11px] rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 transition">SEO & Póster</button>
                  <button onClick={() => copy(pin.pin_id, `${pin.seo_title}\n\n${pin.seo_description}\n\nRuta: ${pin.bridge_route}`)} className="px-2 py-0.5 text-[11px] rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 transition">
                    {copiedId === pin.pin_id ? 'Copiado' : 'Copiar'}
                  </button>
                  <button type="button" onClick={() => onToggleStatus(pin.pin_id)} title="Seguimiento local: no publica en Pinterest" className={`px-2 py-0.5 text-[11px] rounded font-medium transition ${pin.status === 'published' ? 'bg-emerald-950/80 text-emerald-300' : 'bg-zinc-900 text-zinc-500'}`}>
                    {pin.status === 'published' ? 'Marcado publicado (local)' : 'En Cola'}
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {activePin && (
        <div className="fixed inset-0 bg-black/85 backdrop-blur-md z-50 flex items-center justify-center p-4 font-ui" role="presentation" onClick={() => setActivePin(null)}>
          <div role="dialog" aria-modal="true" aria-label={activePin.seo_title} onClick={(e) => e.stopPropagation()} className="bg-[#121214] border border-zinc-700 rounded-2xl max-w-2xl w-full p-5 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start gap-3">
              <div>
                <span className="text-[10px] font-mono-tech px-2 py-0.5 rounded bg-zinc-800 text-zinc-300">{activePin.overlay_badge || 'PIN EDITORIAL'} · SKU {activePin.target_sku_id}</span>
                <h2 className="text-base font-bold text-white mt-1 leading-snug font-grotesque">{activePin.seo_title}</h2>
              </div>
              <button type="button" aria-label="Cerrar" onClick={() => setActivePin(null)} className="w-7 h-7 rounded-full bg-zinc-800 text-zinc-400 hover:text-white flex items-center justify-center transition">
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} aria-hidden="true"><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="aspect-[2/3] rounded-xl overflow-hidden border border-zinc-800 shadow-lg">
                <PinPosterCanvas pin={activePin} index={0} />
              </div>
              <div className="space-y-3 text-xs bg-zinc-900/60 p-3.5 rounded-xl border border-zinc-800 flex flex-col justify-between">
                <div>
                  <div className="text-[10px] font-mono-tech text-zinc-500 uppercase font-bold">Descripción SEO Rica</div>
                  <p className="text-zinc-200 mt-1 whitespace-pre-line leading-relaxed font-ui">{activePin.seo_description}</p>
                </div>
                <div className="space-y-1.5 pt-2 border-t border-zinc-800 text-[11px] font-mono-tech">
                  <div><span className="text-zinc-500">Tablero:</span> <b className="text-zinc-300">{activePin.board_name}</b></div>
                  <div><span className="text-zinc-500">Ruta Puente:</span> <b className="text-amber-300">{activePin.bridge_route}</b></div>
                  <div><span className="text-zinc-500">Impacto Est:</span> <b className="text-emerald-400 tabular-nums">{activePin.simulated_saves} saves</b></div>
                </div>
                <button onClick={() => copy('modal', `${activePin.seo_title}\n\n${activePin.seo_description}\n\nLink: ${activePin.bridge_route}`)} className="w-full py-2 text-xs rounded-xl bg-zinc-100 hover:bg-white text-zinc-900 font-semibold font-mono-tech transition mt-2">
                  {copiedId === 'modal' ? 'Copiado al Portapapeles' : 'Copiar Metadatos SEO'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
