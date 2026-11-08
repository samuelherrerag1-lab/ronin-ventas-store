import React from 'react';
import type { PinterestPinItem } from '../../types/domain';

interface Props {
  pin: PinterestPinItem;
  index: number;
}

const LUXURY_ASSETS = [
  '/generated_images/pin_luxury_chess_gold.png',
  '/generated_images/pin_luxury_setup_oled.png',
  '/generated_images/pin_luxury_watch_espresso.png',
  '/generated_images/nb2_20261102_023928_1de7a6.png',
  '/generated_images/ios17_cyber_luxury_wallpaper.png',
  '/generated_images/pinterest_pin_luxury_desk.png',
  '/generated_images/ios17_titanium_wallpaper.png',
];

const RON_PRODUCT_ASSETS = [
  '/generated_images/pin_ron_3am_blueprint.png',
  '/generated_images/pin_ron_escape_matrix.png',
  '/generated_images/pin_ron_threads_atm.png',
  '/generated_images/ron_frame_laptop.png',
];

const hideOnError = (event: React.SyntheticEvent<HTMLImageElement>) => {
  event.currentTarget.style.visibility = 'hidden';
};

export const PinPosterCanvas: React.FC<Props> = ({ pin, index }) => {
  const isComp = pin.is_competitor_benchmark;
  const isRonProduct = !isComp && (pin.visual_theme?.includes('ron_product') || pin.pin_id === 'pin_003' || pin.pin_id === 'pin_006' || pin.pin_id === 'pin_009');
  const archetype = isComp ? 5 : isRonProduct ? 6 : (index % 5);

  // Archetype 5: Benchmark Competidor (Beige minimalista)
  if (archetype === 5) {
    return (
      <div className="w-full h-full bg-[#F4EFE6] text-[#1C1917] p-3.5 flex flex-col justify-between font-serif relative border border-[#E7E0D2] select-none">
        <div className="flex items-center justify-between border-b border-[#D8CEBC] pb-2 gap-1.5">
          <span className="text-[10px] tracking-[0.15em] uppercase font-sans text-[#78716C] font-semibold truncate min-w-0 pr-1">
            {pin.competitor_source || '@lluvia.creates'}
          </span>
          <span className="text-[8px] px-1.5 py-0.5 rounded-full bg-[#E8E1D5] text-[#57534E] font-sans font-semibold shrink-0 whitespace-nowrap">
            BENCHMARK
          </span>
        </div>
        <div className="my-auto py-2 space-y-1.5">
          <p className="text-[9px] italic text-[#A8A29E] tracking-wider uppercase font-sans">Guía Estética Minimalista</p>
          <h2 className="text-sm leading-snug font-normal text-[#1C1917] tracking-tight">{pin.overlay_headline}</h2>
          <div className="w-8 h-[1px] bg-[#1C1917]/40 my-1" />
          <p className="text-[10px] text-[#57534E] font-sans leading-relaxed line-clamp-3">
            Estrategia de referencia observada en creadores del nicho faceless para análisis de contraste.
          </p>
        </div>
        <div className="pt-2 border-t border-[#D8CEBC] flex items-center justify-between text-[10px] font-sans text-[#78716C]">
          <span>Ebook Digital PDF</span><span className="italic font-serif text-[#1C1917]">Edición 2026</span>
        </div>
      </div>
    );
  }

  // Archetype 6 (30% Balance): Producto Canónico de Ron (ronin_studio 2D)
  if (archetype === 6) {
    const ronImg = pin.image_url || RON_PRODUCT_ASSETS[index % RON_PRODUCT_ASSETS.length];
    return (
      <div className="w-full h-full relative overflow-hidden select-none bg-black flex flex-col justify-between font-ui">
        <img src={ronImg} alt={pin.seo_title} onError={hideOnError} className="absolute inset-0 w-full h-full object-cover object-top brightness-[0.95]" />
        <div className="relative z-10 p-3 flex justify-between items-center gap-1.5 bg-gradient-to-b from-black/80 via-black/30 to-transparent">
          <span className="text-[8px] font-mono-tech font-bold px-2 py-0.5 rounded bg-[#E07A5F] text-white uppercase tracking-wider shadow shrink-0">
            {pin.overlay_badge || 'PRODUCTO OFICIAL'}
          </span>
          <span className="text-[8px] font-mono-tech font-bold px-2 py-0.5 rounded bg-black/85 text-emerald-300 border border-emerald-500/40 shrink-0">{pin.target_sku_id}</span>
        </div>
        <div className="relative z-10 bg-gradient-to-t from-black via-black/95 to-transparent pt-10 pb-3 px-3 space-y-1">
          <h2 className="text-[11px] sm:text-xs font-black uppercase text-white leading-tight drop-shadow-md tracking-tight line-clamp-2 font-display">
            {pin.overlay_headline}
          </h2>
          <div className="inline-flex items-center gap-1 bg-black/80 px-2 py-0.5 rounded text-[8px] font-mono-tech text-[#E07A5F] border border-[#E07A5F]/40">
            <span>ACCESO INMEDIATO</span><span>•</span><span>@ronOverthinks</span>
          </div>
        </div>
      </div>
    );
  }

  const bgImg = pin.image_url || LUXURY_ASSETS[index % LUXURY_ASSETS.length];

  // Archetype 0: Ficha de Ajedrez Obsidiana & Oro (Estrategia Asimétrica)
  if (archetype === 0) {
    return (
      <div className="w-full h-full relative overflow-hidden select-none bg-black font-ui">
        <img src={bgImg} alt={pin.seo_title} onError={hideOnError} className="w-full h-full object-cover brightness-[0.85]" />
        <div className="absolute inset-0 bg-gradient-to-t from-black via-black/45 to-black/35 p-3.5 flex flex-col justify-between">
          <div className="flex justify-center">
            <span className="text-[8px] font-mono-tech font-bold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 uppercase tracking-widest shadow-lg">
              ESTRATEGIA ASIMÉTRICA • PRIVADA
            </span>
          </div>
          <div className="space-y-1.5 mb-1.5">
            <div className="inline-block bg-[#F59E0B] text-black px-2 py-0.5 text-[9px] font-black uppercase tracking-wider rounded font-mono-tech">{pin.overlay_badge || 'JAQUE MATE DIGITAL'}</div>
            <h2 className="text-xs sm:text-sm font-black uppercase text-white leading-tight drop-shadow-xl tracking-tight font-display">{pin.overlay_headline}</h2>
            <p className="text-[9px] text-zinc-300 line-clamp-1 leading-snug">Estrategia asimétrica y análisis de conversión</p>
          </div>
        </div>
      </div>
    );
  }

  // Archetype 1: Setup Nocturno OLED / Infografía Dark Noir
  if (archetype === 1) {
    return (
      <div className="w-full h-full relative overflow-hidden select-none bg-[#090b10] border border-zinc-800 font-ui">
        <img src={bgImg} alt={pin.seo_title} onError={hideOnError} className="w-full h-full object-cover brightness-[0.45] absolute inset-0" />
        <div className="relative z-10 w-full h-full p-3.5 flex flex-col justify-between bg-black/55 backdrop-blur-[2px]">
          <div>
            <div className="flex items-center justify-between text-[8px] font-mono-tech text-zinc-400 pb-1.5 border-b border-zinc-800">
              <span className="text-amber-400 font-bold uppercase tracking-wider">Protocolo 3 Fases</span><span>SETUP MINIMALISTA</span>
            </div>
            <h2 className="text-xs sm:text-sm font-black uppercase text-white tracking-tight mt-1.5 mb-1 leading-snug drop-shadow-md font-grotesque">{pin.overlay_headline}</h2>
          </div>
          <div className="space-y-1 my-auto font-ui">
            {[{ num: '01', title: 'Infiltrar Nicho', desc: 'Identificar dolor urgente sin rostro' }, { num: '02', title: 'Desplegar App', desc: 'Micro-herramienta con doble checkout' }, { num: '03', title: 'Tráfico Silencioso', desc: 'Rutas puente a Gumroad/Hotmart' }].map((s) => (
              <div key={s.num} className="bg-black/80 border border-zinc-700/80 rounded-lg p-1.5 flex items-start gap-2">
                <span className="text-[9px] font-mono-tech font-black text-amber-400 bg-amber-500/10 px-1 py-0.2 rounded border border-amber-500/20">{s.num}</span>
                <div className="min-w-0"><p className="text-[10px] font-bold text-zinc-100 leading-tight">{s.title}</p><p className="text-[8px] text-zinc-400 leading-tight truncate">{s.desc}</p></div>
              </div>
            ))}
          </div>
          <div className="pt-1.5 border-t border-zinc-800/80 flex items-center justify-between text-[8px] font-mono-tech text-zinc-400">
            <span className="text-emerald-400 font-semibold">100% OPERABLE</span><span>SIN SEGUIDORES</span>
          </div>
        </div>
      </div>
    );
  }

  // Archetype 2: Reloj Negro Mate & Contraste Psicológico
  if (archetype === 2) {
    return (
      <div className="w-full h-full relative overflow-hidden select-none bg-black font-ui">
        <img src={bgImg} alt={pin.seo_title} onError={hideOnError} className="w-full h-full object-cover brightness-[0.4] absolute inset-0" />
        <div className="relative z-10 w-full h-full flex flex-col justify-between">
          <div className="flex-1 bg-gradient-to-b from-rose-950/80 to-transparent p-3.5 border-b border-rose-900/30 flex flex-col justify-between">
            <span className="text-[8px] font-mono-tech font-bold text-rose-400 uppercase tracking-wider flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-rose-500" />EL 95% HACE ESTO (TRAMPA):</span>
            <p className="text-[11px] text-rose-200/90 font-medium leading-snug my-0.5">Vender plantillas genéricas de Canva a $3 y mendigar DMs.</p>            <span className="text-[8px] font-mono-tech text-rose-400/80">Margen neto: &lt; 5%</span>
          </div>
          <div className="h-5 -my-2.5 z-10 flex justify-center items-center">
            <span className="px-2.5 py-0.5 bg-black border border-zinc-700 text-amber-300 font-mono-tech text-[8px] font-bold rounded-full shadow-md uppercase">VS SISTEMA SILENCIOSO</span>
          </div>
          <div className="flex-1 bg-gradient-to-t from-emerald-950/90 to-transparent p-3.5 border-t border-emerald-900/30 flex flex-col justify-between">
            <span className="text-[8px] font-mono-tech font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />ALTO MARGEN:</span>
            <p className="text-[11px] text-emerald-100 font-semibold leading-snug my-0.5 font-grotesque">{pin.overlay_headline}</p>
            <div className="flex items-center justify-between text-[8px] font-mono-tech text-emerald-400"><span>Doble Checkout Nequi + USD</span><span className="font-bold">92% Margen Neto</span></div>
          </div>
        </div>
      </div>
    );
  }

  // Archetype 3: Terminal Esmeralda / Blueprint
  if (archetype === 3) {
    return (
      <div className="w-full h-full relative overflow-hidden select-none bg-[#0c0d12] border border-zinc-800 font-ui">
        <img src={bgImg} alt={pin.seo_title} onError={hideOnError} className="w-full h-full object-cover brightness-[0.35] absolute inset-0" />
        <div className="relative z-10 w-full h-full bg-[radial-gradient(#ffffff12_1px,transparent_1px)] [background-size:14px_14px] p-3.5 flex flex-col justify-between text-zinc-100">
          <div>
            <div className="flex items-center justify-between text-[8px] font-mono-tech text-cyan-400 pb-1.5 border-b border-zinc-800/80"><span className="font-bold uppercase tracking-wider">Flujo de Conversión</span><span>BLUEPRINT 2026</span></div>
            <h2 className="text-xs sm:text-sm font-black uppercase text-white mt-1.5 leading-tight tracking-tight drop-shadow-md font-grotesque">{pin.overlay_headline}</h2>
          </div>
          <div className="my-auto py-1 space-y-1 font-mono-tech">
            <div className="p-1.5 rounded bg-black/70 border border-zinc-700 text-center text-[10px] font-semibold text-zinc-200">Tráfico Frío Anzuelo (Threads + Pines)</div>
            <div className="flex justify-center text-cyan-400 leading-none">
              <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} aria-hidden="true"><path d="M12 5v14m0 0 5-5m-5 5-5-5" strokeLinecap="round" strokeLinejoin="round" /></svg>
            </div>
            <div className="p-1.5 rounded bg-cyan-950/70 border border-cyan-500/40 text-center text-[10px] font-bold text-cyan-200">55 Rutas Puente Semánticas Stan Pro</div>
            <div className="flex justify-center text-emerald-400 leading-none">
              <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} aria-hidden="true"><path d="M12 5v14m0 0 5-5m-5 5-5-5" strokeLinecap="round" strokeLinejoin="round" /></svg>
            </div>
            <div className="p-1.5 rounded bg-emerald-950/70 border border-emerald-500/40 text-center text-[10px] font-bold text-emerald-300">Checkout Directo Hotmart + Gumroad</div>
          </div>
          <div className="pt-1.5 border-t border-zinc-800/80 flex items-center justify-between text-[8px] font-mono-tech text-zinc-400"><span>LATENCIA: 0.12s</span><span className="text-cyan-400 font-bold">STEALTH 96/100</span></div>
        </div>
      </div>
    );
  }

  // Archetype 4: Penthouse / Luxury Desk con Notificación Flotante
  return (
    <div className="w-full h-full relative overflow-hidden select-none bg-zinc-950 font-ui">
      <img src={bgImg} alt={pin.seo_title} onError={hideOnError} className="w-full h-full object-cover brightness-[0.7]" />
      <div className="absolute inset-0 bg-gradient-to-t from-black via-black/45 to-transparent p-3.5 flex flex-col justify-between">
        <div className="text-center">
          <span className="text-[8px] font-mono-tech tracking-widest uppercase px-2 py-0.5 rounded bg-black/60 text-zinc-300 border border-white/10 font-bold">MUESTRA — MONITOR DE VENTAS (SIMULACIÓN)</span>
          <h2 className="text-xs sm:text-sm font-black uppercase text-white mt-1.5 leading-tight drop-shadow-md font-grotesque">{pin.overlay_headline}</h2>
        </div>
        <div className="backdrop-blur-xl bg-[#1c1c1e]/90 border border-white/15 p-2.5 rounded-xl shadow-2xl my-auto space-y-0.5">
          <div className="flex items-center justify-between text-[9px] text-white/70"><span className="font-bold text-[#FF90E8] uppercase tracking-wider font-mono-tech">Gumroad</span><span className="font-mono-tech text-white/50">hace 3m</span></div>
          <p className="text-[11px] font-bold text-white leading-tight font-display">$47.00 USD</p>
          <p className="text-[9px] text-zinc-300 truncate">Bóveda de Sistemas & Micro-Apps</p>
        </div>
        <div className="text-center"><span className="text-[8px] font-mono-tech text-emerald-400 bg-black/70 px-2 py-0.5 rounded-full border border-emerald-500/30">FLUJO SILENCIOSO • LATAM</span></div>
      </div>
    </div>
  );
};
