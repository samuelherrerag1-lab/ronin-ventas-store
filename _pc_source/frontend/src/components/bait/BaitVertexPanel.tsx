import React from 'react';

export interface BaitGeneratedImage {
  url: string;
  latency?: number;
  elapsed?: number;
  model?: string;
  cost?: number;
  spent?: number;
}

interface Props {
  prompt: string;
  onPromptChange: (value: string) => void;
  aspectRatio: string;
  onAspectChange: (value: string) => void;
  generatedImg: BaitGeneratedImage | null;
  vertexError: string | null;
  generating: boolean;
  onGenerate: () => void;
  onPickWallpaper: (url: string) => void;
  vertexModel?: string | null;
  vertexRegion?: string | null;
}

export const VERTEX_PROMPT_PRESETS = [
  'Ron in oversized terracotta hoodie #E07A5F with ojeras looking at glowing green Gumroad notification at 3AM, dark moody comic ink',
  'Obsidian desk, glowing neon green terminal graph, dark luxury aesthetic, gold rim lighting',
  'Minimalist matte black coffee cup next to iPad sales analytics graph, moody cinematic shadows',
];
const PRESETS = VERTEX_PROMPT_PRESETS;

const CHIPS = [
  { src: '/generated_images/ios17_editorial_dark_wallpaper.png', alt: 'OLED Dark', title: 'OLED Dark Wallpaper' },
  { src: '/generated_images/ron_avatar_profile.png', alt: 'Ron Deadpan', title: 'Ron Deadpan' },
  { src: '/generated_images/ron_tired.png', alt: 'Ron Ojeras', title: 'Ron Ojeras 3AM' },
  { src: '/generated_images/ron_frame_laptop.png', alt: 'Ron Laptop', title: 'Ron Laptop' },
];

const formatNum = (value: number | undefined | null, digits: number): string =>
  typeof value === 'number' ? value.toFixed(digits) : '—';

export const BaitVertexPanel: React.FC<Props> = ({
  prompt,
  onPromptChange,
  aspectRatio,
  onAspectChange,
  generatedImg,
  vertexError,
  generating,
  onGenerate,
  onPickWallpaper,
  vertexModel,
  vertexRegion,
}) => (
  <div className="lg:col-span-4 bg-[#0c0c13]/90 border border-white/[0.08] rounded-2xl p-4 space-y-3 shadow-xl order-3">
    <div className="border-b border-white/[0.07] pb-2 flex items-center justify-between gap-2">
      <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400 font-mono">2. Vertex AI — Nano Banana 2</span>
      <span
        className="text-[9px] px-2 py-0.5 rounded bg-zinc-950 border border-white/10 text-emerald-300 font-mono max-w-[190px] truncate"
        title={`Modelo: ${vertexModel ?? 'sin verificar'} | Región: ${vertexRegion ?? 'sin verificar'}`}
      >
        {vertexModel ?? 'modelo sin verificar'}
        {vertexRegion ? ` · ${vertexRegion}` : ''}
      </span>
    </div>
    <div className="grid grid-cols-4 gap-1.5 bg-zinc-950/80 p-1.5 rounded-xl border border-white/5">
      {CHIPS.map((chip) => (
        <button key={chip.src} type="button" onClick={() => onPickWallpaper(chip.src)} title={chip.title} aria-label={`Usar fondo ${chip.title}`}>
          <img src={chip.src} alt={chip.alt} className="h-12 w-full object-cover rounded border border-white/10 hover:border-emerald-500/50 transition" />
        </button>
      ))}
    </div>
    <div className="space-y-1">
      {PRESETS.map((preset, index) => (
        <button key={index} type="button" onClick={() => onPromptChange(preset)} className="w-full text-left text-[9.5px] p-1.5 rounded bg-zinc-950 hover:bg-zinc-900 border border-white/[0.07] text-zinc-300 truncate font-mono">
          #{index + 1}: {preset}
        </button>
      ))}
    </div>
    <div>
      <label htmlFor="vertex-prompt" className="text-[9.5px] text-zinc-400 font-mono">Prompt Fotografico Vertex AI</label>
      <textarea id="vertex-prompt" value={prompt} onChange={(e) => onPromptChange(e.target.value)} rows={2} className="w-full bg-zinc-950 border border-white/10 rounded-lg p-2 text-xs text-zinc-200 mt-1" />
    </div>
    <div className="flex items-center justify-between text-xs">
      <span className="text-[10px] text-zinc-400 font-mono">Proporción:</span>
      <div className="flex gap-1">
        {['9:16', '3:4', '1:1'].map((ratio) => (
          <button key={ratio} type="button" onClick={() => onAspectChange(ratio)} className={`text-[10px] px-2.5 py-1 rounded font-mono ${aspectRatio === ratio ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : 'bg-zinc-950 text-zinc-400'}`}>
            {ratio}
          </button>
        ))}
      </div>
    </div>
    {generatedImg && (
      <div className="p-2 bg-zinc-950 rounded-xl border border-emerald-500/30 space-y-1">
        <div className="grid grid-cols-2 gap-1 text-[9px] text-zinc-300 font-mono">
          <span>Intento: {formatNum(generatedImg.elapsed ?? generatedImg.latency, 1)}s</span>
          <span className="text-right">Costo: {generatedImg.cost != null ? `$${formatNum(generatedImg.cost, 4)}` : '—'}</span>
          <span className="truncate" title={generatedImg.model ?? 'modelo sin reportar'}>Modelo: {generatedImg.model ?? '—'}</span>
          <span className="text-right">Gasto total: {generatedImg.spent != null ? `$${formatNum(generatedImg.spent, 2)}` : '—'}</span>
        </div>
        <img src={generatedImg.url} alt="Resultado de Vertex AI" className="w-full h-24 object-cover rounded border border-white/10" onError={(e) => { e.currentTarget.style.visibility = 'hidden'; }} />
      </div>
    )}
    {vertexError && <div role="alert" className="p-2 bg-red-950/40 border border-red-800/50 rounded-lg text-[11px] text-red-300 leading-relaxed">{vertexError}</div>}
    <button type="button" disabled={generating} onClick={onGenerate} className="w-full py-2.5 px-3 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition shadow disabled:opacity-50">
      {generating ? 'Generando Fondo Real...' : 'Generar Fondo OLED con Nano Banana 2'}
    </button>
  </div>
);
