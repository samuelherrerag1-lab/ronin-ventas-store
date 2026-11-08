import React, { useState } from 'react';
import { IosBaitFrame } from './IosBaitFrame';
import { renderIosPng } from '../../api/client';
import type { FinopsSummary } from '../../types/domain';
import { BaitVertexPanel, VERTEX_PROMPT_PRESETS, type BaitGeneratedImage } from './BaitVertexPanel';

export interface BaitStudioViewProps {
  onCreateBaitPost: (data: {
    headline_metric: string; sub_metric: string; notifications: string[];
    widget_type: string; post_text: string; target_sku_id: string;
  }) => Promise<unknown> | void;
  onGenerateVertex: (prompt: string, aspectRatio: string) => Promise<{
    image_url: string;
    status?: string;
    latency_sec?: number;
    elapsed_attempt_sec?: number;
    model?: string;
    estimated_cost_usd?: number;
    spent_total_usd?: number;
  }>;
  finops?: FinopsSummary | null;
  vertexModel?: string | null;
  vertexRegion?: string | null;
  availableSkus?: { sku_id: string; title: string }[];
}

const WALLPAPERS = [
  { label: 'OLED Editorial', url: '/generated_images/ios17_editorial_dark_wallpaper.png' },
  { label: 'Titanio iOS 17', url: '/generated_images/ios17_titanium_wallpaper.png' },
  { label: 'Ron 3AM Laptop', url: '/generated_images/ron_frame_laptop.png' },
  { label: 'Penthouse 3AM', url: '/generated_images/ios17_cyber_luxury_wallpaper.png' },
];

export const BaitStudioView: React.FC<BaitStudioViewProps> = ({
  onCreateBaitPost, onGenerateVertex, finops, vertexModel, vertexRegion,
  availableSkus = [
    { sku_id: 'E01', title: 'Manual Faceless Threads ($19 USD)' },
    { sku_id: 'B01', title: 'Boveda 500 Hooks Cinicos ($27 USD)' },
    { sku_id: 'A01', title: 'Forjador Hooks Micro-App ($19 USD)' },
  ],
}) => {
  const [widgetType, setWidgetType] = useState('ios_lockscreen');
  const [wallpaperUrl, setWallpaperUrl] = useState(WALLPAPERS[0].url);
  const [headline, setHeadline] = useState('$418.50 USD');
  const [subMetric, setSubMetric] = useState('+37 ventas hoy · 91% margen');
  const [timestamp, setTimestamp] = useState('07:12');
  const [dateLabel, setDateLabel] = useState('domingo, 2 de noviembre');
  const [notif1, setNotif1] = useState('$19.00 USD — Boveda de 500 Hooks Cinicos');
  const [notif2, setNotif2] = useState('Hotmart • Comision aprobada: $79.800 COP (Nequi PSE)');
  const [notif3, setNotif3] = useState('$28.00 USD — Maquina Silenciosa PDF + Order Bump');
  const [postText, setPostText] = useState('La mayoria pierde meses programando apps cuando un sistema HTML de 1 archivo genera esto mientras duermes.');
  const [targetSku, setTargetSku] = useState('E01');
  const [isInjecting, setIsInjecting] = useState(false);
  const [injectSuccess, setInjectSuccess] = useState(false);
  const [injectError, setInjectError] = useState<string | null>(null);
  const [isRenderingPng, setIsRenderingPng] = useState(false);
  const [renderedPng, setRenderedPng] = useState<{ image_url: string; filename: string; resolution?: string } | null>(null);
  const [pngError, setPngError] = useState<string | null>(null);
  const [prompt, setPrompt] = useState(VERTEX_PROMPT_PRESETS[0]);
  const [aspectRatio, setAspectRatio] = useState('9:16');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedImg, setGeneratedImg] = useState<BaitGeneratedImage | null>(null);
  const [vertexError, setVertexError] = useState<string | null>(null);

  const handleInject = async () => {
    setIsInjecting(true); setInjectSuccess(false); setInjectError(null);
    try {
      await onCreateBaitPost({
        headline_metric: headline, sub_metric: subMetric,
        notifications: [notif1, notif2, notif3].filter(Boolean),
        widget_type: widgetType, post_text: postText, target_sku_id: targetSku,
      });
      setInjectSuccess(true); window.setTimeout(() => setInjectSuccess(false), 3000);
    } catch (error) {
      setInjectError(error instanceof Error ? error.message : String(error));
    } finally { setIsInjecting(false); }
  };

  const handleRenderPng = async () => {
    setIsRenderingPng(true); setPngError(null);
    try {
      const res = await renderIosPng({
        headline_metric: headline, sub_metric: subMetric,
        notifications: [notif1, notif2, notif3].filter(Boolean), timestamp_label: timestamp, date_label: dateLabel,
        widget_type: widgetType, wallpaper_filename: wallpaperUrl.split('/').pop() || 'ios17_editorial_dark_wallpaper.png',
      });
      setRenderedPng(res);
    } catch (error) {
      setPngError(error instanceof Error ? error.message : 'Error en Retina Renderer');
    } finally { setIsRenderingPng(false); }
  };

  const handleGenerate = async () => {
    setIsGenerating(true); setVertexError(null);
    try {
      const res = await onGenerateVertex(prompt, aspectRatio);
      if (!res.image_url) {
        setVertexError('Vertex no devolvió image_url. No se muestra un fondo de reemplazo para no simular un resultado.');
        return;
      }
      setGeneratedImg({
        url: res.image_url,
        latency: res.latency_sec,
        elapsed: res.elapsed_attempt_sec,
        model: res.model,
        cost: res.estimated_cost_usd,
        spent: res.spent_total_usd,
      });
      setWallpaperUrl(res.image_url);
    } catch (error) {
      setVertexError(error instanceof Error ? error.message : String(error));
    } finally { setIsGenerating(false); }
  };

  return (
    <div className="space-y-4 text-zinc-100">
      <div className="pb-3 border-b border-white/[0.08] flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 bg-amber-500/15 text-amber-300 rounded-md border border-amber-500/30 text-[10px] font-mono uppercase tracking-wider">iOS 17.5 Screenshot Lab</span>
          </div>
          <h1 className="text-lg sm:text-xl font-bold tracking-tight text-white">Laboratorio de Capturas "Anzuelo" & Vertex AI Nano Banana 2</h1>
          <p className="text-xs text-zinc-400 mt-1">Captura de pantalla pura iOS 17.5 (393×852 px sin marcos físicos) con fondos OLED de Vertex AI.</p>
        </div>
        <div className="flex flex-col items-start sm:items-end gap-1 text-[10px] font-mono-tech bg-[#0d0d14] border border-white/10 px-3 py-1.5 rounded-xl">
          <span className="flex items-center gap-1.5">
            <span className="text-zinc-400">Vertex FinOps:</span>
            {finops ? (
              <>
                <span className="text-emerald-400 font-bold tabular-nums">${finops.total_spent_usd.toFixed(2)}</span>
                <span className="text-zinc-600">/</span>
                <span className="text-zinc-400 tabular-nums">${finops.circuit_breaker_limit_usd.toFixed(2)} USD</span>
              </>
            ) : (
              <span className="text-amber-300 font-bold">sin ledger reportado</span>
            )}
          </span>
          <span className="text-zinc-500 truncate max-w-[260px]" title={finops?.project_id ?? 'Proyecto Vertex sin verificar'}>
            {finops?.project_id ?? 'proyecto Vertex sin verificar'}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* Columna 1: Controles y Parámetros */}
        <div className="lg:col-span-4 bg-[#0c0c13]/90 border border-white/[0.08] rounded-2xl p-4 space-y-3 shadow-xl order-2 lg:order-1">
          <div className="flex items-center justify-between border-b border-white/[0.07] pb-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-amber-400 font-mono">1. Configuración iOS</span>
          </div>
          <div className="flex flex-wrap gap-1">
            {[{ id: 'ios_lockscreen', label: 'Lockscreen' }, { id: 'stripe_gumroad_dashboard', label: 'Stripe Live' }, { id: 'iphone_note_3am', label: 'Apple Notes' }].map((t) => (
              <button key={t.id} onClick={() => setWidgetType(t.id)} className={`text-[11px] px-3 py-1.5 rounded-lg font-mono transition ${widgetType === t.id ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold' : 'bg-zinc-950 text-zinc-400 border border-white/5'}`}>{t.label}</button>
            ))}
          </div>
          <div className="bg-zinc-950/90 border border-white/[0.06] rounded-xl p-2.5 space-y-1.5">
            <span className="text-[10px] font-mono text-zinc-400 uppercase">Fondo OLED Activo:</span>
            <div className="flex flex-wrap gap-1.5">
              {WALLPAPERS.map((w) => (
                <button key={w.url} onClick={() => setWallpaperUrl(w.url)} className={`text-[10px] px-2.5 py-1 rounded-lg font-mono transition ${wallpaperUrl === w.url ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-semibold' : 'bg-zinc-900 text-zinc-400'}`}>{w.label}</button>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-3 gap-2 text-xs">
            <div><label htmlFor="bait-hora" className="text-[9px] text-zinc-400 font-mono">Hora</label><input id="bait-hora" value={timestamp} onChange={(e) => setTimestamp(e.target.value)} className="w-full bg-zinc-950 border border-white/10 rounded px-2 py-1.5 text-zinc-200 font-mono text-xs" /></div>
            <div><label htmlFor="bait-metrica" className="text-[9px] text-zinc-400 font-mono">Métrica</label><input id="bait-metrica" value={headline} onChange={(e) => setHeadline(e.target.value)} className="w-full bg-zinc-950 border border-white/10 rounded px-2 py-1.5 text-emerald-400 font-mono font-bold text-xs" /></div>
            <div><label htmlFor="bait-submetrica" className="text-[9px] text-zinc-400 font-mono">Sub-métrica</label><input id="bait-submetrica" value={subMetric} onChange={(e) => setSubMetric(e.target.value)} className="w-full bg-zinc-950 border border-white/10 rounded px-2 py-1.5 text-zinc-200 text-xs truncate" /></div>
          </div>
          <div className="space-y-1.5 text-xs">
            <input aria-label="Notificación 1 de la captura" value={notif1} onChange={(e) => setNotif1(e.target.value)} className="w-full bg-zinc-950 border border-white/10 rounded px-2.5 py-1.5 text-zinc-200 text-[11px]" />
            <input aria-label="Notificación 2 de la captura" value={notif2} onChange={(e) => setNotif2(e.target.value)} className="w-full bg-zinc-950 border border-white/10 rounded px-2.5 py-1.5 text-zinc-200 text-[11px]" />
            <input aria-label="Notificación 3 de la captura" value={notif3} onChange={(e) => setNotif3(e.target.value)} className="w-full bg-zinc-950 border border-white/10 rounded px-2.5 py-1.5 text-zinc-200 text-[11px]" />
          </div>
          <button type="button" disabled={isRenderingPng} onClick={handleRenderPng} className="w-full py-2.5 px-3 rounded-xl text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white transition shadow flex items-center justify-center gap-1.5">
            {isRenderingPng ? 'Renderizando Retina 3x...' : 'Exportar PNG Retina Real (1179×2556)'}
          </button>
          {renderedPng && (
            <a href={renderedPng.image_url} target="_blank" rel="noreferrer" download={renderedPng.filename} className="block text-center py-2 px-3 rounded-xl text-xs font-bold bg-zinc-950 text-emerald-400 border border-emerald-500/50 transition">
              Descargar {renderedPng.resolution ? renderedPng.resolution.split(' ')[0] : '1179×2556'} PNG
            </a>
          )}
          {pngError && <div className="p-2 bg-red-950/40 border border-red-800/50 rounded-lg text-[11px] text-red-300">{pngError}</div>}
        </div>

        {/* Columna 2: Preview Legible Escala >= 0.85 sin marcos ni scroll interno */}
        <div className="lg:col-span-4 bg-[#0c0c13]/90 border border-white/[0.08] rounded-2xl p-4 space-y-3 shadow-xl flex flex-col items-center order-1 lg:order-2">
          <div className="w-full flex items-center justify-between border-b border-white/[0.07] pb-2 text-[10px] font-mono text-zinc-400">
            <span className="text-amber-400 uppercase tracking-wider font-semibold">Captura Plana 1:1</span>
            <span className="text-emerald-400 font-semibold">Escala 0.76x/0.88x · Legible</span>
          </div>
          {/* Contenedor responsive: 393x852 escalado a 0.76x en móvil y 0.88x desde sm */}
          <div className="w-[299px] h-[648px] sm:w-[346px] sm:h-[750px] max-w-full relative shrink-0 shadow-2xl rounded-[32px] overflow-hidden border border-white/15 bg-black">
            <div className="w-[393px] h-[852px] origin-top-left transform scale-[0.76] sm:scale-[0.88]">
              <IosBaitFrame wallpaperUrl={wallpaperUrl} config={{ widget_type: widgetType as any, headline_metric: headline, sub_metric: subMetric, notifications: [notif1, notif2, notif3].filter(Boolean), timestamp_label: timestamp, date_label: dateLabel }} />
            </div>
          </div>
          <div className="w-full space-y-2 pt-1">
            <div className="flex justify-between items-center text-[10px] text-zinc-400 font-mono">
              <span>Copy Threads</span>
              <select value={targetSku} onChange={(e) => setTargetSku(e.target.value)} className="bg-zinc-950 border border-white/10 rounded px-2 py-0.5 text-zinc-200 text-[10px]">
                {availableSkus.map((s) => (<option key={s.sku_id} value={s.sku_id}>{s.sku_id} - {s.title.split('(')[0]}</option>))}
              </select>
            </div>
            <textarea value={postText} onChange={(e) => setPostText(e.target.value)} rows={2} className="w-full bg-zinc-950 border border-white/10 rounded-lg p-2 text-[11px] text-zinc-200" />
            <button
              type="button"
              disabled={isInjecting}
              onClick={handleInject}
              className="w-full py-2.5 px-3 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-400 text-zinc-950 transition shadow disabled:opacity-60"
            >
              {isInjecting ? 'Inyectando...' : injectSuccess ? 'Añadido al feed de Threads' : 'Inyectar al Feed de Threads'}
            </button>
            {injectError && <div role="alert" className="p-2 rounded-lg bg-red-950/40 border border-red-800/50 text-[11px] text-red-300 leading-relaxed">{injectError}</div>}
          </div>
        </div>

        <BaitVertexPanel
          prompt={prompt}
          onPromptChange={setPrompt}
          aspectRatio={aspectRatio}
          onAspectChange={setAspectRatio}
          generatedImg={generatedImg}
          vertexError={vertexError}
          generating={isGenerating}
          onGenerate={handleGenerate}
          onPickWallpaper={setWallpaperUrl}
          vertexModel={vertexModel}
          vertexRegion={vertexRegion}
        />
      </div>
    </div>
  );
};
