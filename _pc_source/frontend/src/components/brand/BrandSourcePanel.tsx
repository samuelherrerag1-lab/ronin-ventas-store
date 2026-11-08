/** Panel 01: entrada de imagen local, zoom de recorte y fondo del avatar. */

import React, { useRef, useState } from 'react';
import type { AvatarBackground, ImageMeta } from './brandSpecs';
import { AVATAR_BACKGROUNDS, formatBytes, MAX_FILE_BYTES } from './brandSpecs';
import { AlertIcon, SlidersIcon, TrashIcon, UploadIcon } from './StudioIcons';

interface BrandSourcePanelProps {
  image: HTMLImageElement | null;
  meta: ImageMeta | null;
  error: string | null;
  decoding: boolean;
  zoom: number;
  background: AvatarBackground;
  onFile: (file: File) => void;
  onZoom: (zoom: number) => void;
  onBackground: (background: AvatarBackground) => void;
  onClear: () => void;
}

const isImageBackgroundLight = (background: AvatarBackground): boolean => background.id === 'blanco';

export const BrandSourcePanel: React.FC<BrandSourcePanelProps> = ({
  image, meta, error, decoding, zoom, background, onFile, onZoom, onBackground, onClear,
}) => {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [dragging, setDragging] = useState(false);

  const pick = () => inputRef.current?.click();

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setDragging(false);
    const file = event.dataTransfer.files && event.dataTransfer.files[0];
    if (file) onFile(file);
  };

  const percent = Math.round(zoom * 100);

  return (
    <section aria-labelledby="brand-source-title" className="bg-[#090b10] border border-white/[0.08] rounded-2xl p-4 space-y-4">
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-[10px] font-mono-tech font-bold uppercase tracking-wider text-[#E07A5F]">01 / Fuente</p>
          <h2 id="brand-source-title" className="text-sm font-bold text-white font-grotesque mt-0.5">Imagen y recorte</h2>
        </div>
        <span className="text-[9px] font-mono-tech text-zinc-500 border border-white/[0.08] rounded px-1.5 py-0.5 tabular-nums">MÁX {formatBytes(MAX_FILE_BYTES)}</span>
      </div>

      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        tabIndex={-1}
        aria-hidden="true"
        className="hidden"
        onChange={(event) => {
          const file = event.target.files && event.target.files[0];
          event.target.value = '';
          if (file) onFile(file);
        }}
      />

      <div
        onDragOver={(event) => { event.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        className={`rounded-xl border border-dashed transition-colors ${dragging ? 'border-[#E07A5F] bg-[#E07A5F]/[0.06]' : 'border-white/15 bg-black/40'}`}
      >
        {image ? (
          <div className="relative">
            <img
              src={image.src}
              alt={meta ? `Vista previa de ${meta.name}` : 'Vista previa de la imagen cargada'}
              className="w-full max-h-56 object-contain rounded-xl bg-black/60"
            />
            {decoding && (
              <div className="absolute inset-0 flex items-center justify-center bg-black/70 rounded-xl">
                <span className="text-[10px] font-mono-tech text-[#E07A5F]">PROCESANDO…</span>
              </div>
            )}
          </div>
        ) : (
          <div className="px-4 py-6 flex flex-col items-center text-center gap-2">
            <span className="w-10 h-10 rounded-xl border border-white/10 bg-white/[0.03] flex items-center justify-center text-zinc-400">
              <UploadIcon className="w-5 h-5" />
            </span>
            <p className="text-[11px] text-zinc-300 leading-snug">
              Arrastra una imagen aquí o selecciónala desde el disco.
            </p>
            <p className="text-[10px] text-zinc-500 font-mono-tech">PNG · JPG · WEBP · GIF · AVIF</p>
          </div>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <button
          type="button"
          onClick={pick}
          disabled={decoding}
          className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-[#E07A5F] text-black text-[11px] font-mono-tech font-bold hover:bg-[#ea8b72] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#E07A5F] focus-visible:ring-offset-2 focus-visible:ring-offset-[#090b10] disabled:opacity-50 transition"
        >
          <UploadIcon className="w-3.5 h-3.5" />
          {image ? 'Cambiar imagen' : 'Subir imagen'}
        </button>
        <button
          type="button"
          onClick={onClear}
          disabled={!image && !error}
          className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl border border-white/10 bg-white/[0.03] text-[11px] font-mono-tech text-zinc-300 hover:text-white hover:border-white/25 focus:outline-none focus-visible:ring-2 focus-visible:ring-white/40 disabled:opacity-40 disabled:cursor-not-allowed transition"
        >
          <TrashIcon className="w-3.5 h-3.5" />
          Quitar
        </button>
        <button
          type="button"
          onClick={() => onZoom(1)}
          disabled={percent === 100}
          className="ml-auto text-[10px] font-mono-tech text-zinc-500 hover:text-zinc-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-white/40 rounded px-1.5 py-1 disabled:opacity-30 disabled:cursor-not-allowed transition"
        >
          Reset zoom
        </button>
      </div>

      {error && (
        <div role="alert" className="flex items-start gap-2 rounded-xl border border-rose-500/35 bg-rose-500/[0.08] p-2.5">
          <AlertIcon className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
          <p className="text-[11px] text-rose-200 leading-snug">{error}</p>
        </div>
      )}

      {meta && (
        <dl className="grid grid-cols-3 gap-2 text-[10px] font-mono-tech">
          <div className="bg-black/40 border border-white/[0.06] rounded-lg p-2 min-w-0">
            <dt className="text-zinc-500 uppercase text-[9px]">Archivo</dt>
            <dd className="text-zinc-200 truncate mt-0.5" title={meta.name}>{meta.name}</dd>
          </div>
          <div className="bg-black/40 border border-white/[0.06] rounded-lg p-2">
            <dt className="text-zinc-500 uppercase text-[9px]">Peso</dt>
            <dd className="text-zinc-200 mt-0.5 tabular-nums">{formatBytes(meta.size)}</dd>
          </div>
          <div className="bg-black/40 border border-white/[0.06] rounded-lg p-2">
            <dt className="text-zinc-500 uppercase text-[9px]">Original</dt>
            <dd className="text-zinc-200 mt-0.5 tabular-nums">{meta.width}×{meta.height}</dd>
          </div>
        </dl>
      )}

      <div className="space-y-2">
        <div className="flex items-center justify-between gap-2">
          <label htmlFor="brand-zoom" className="flex items-center gap-1.5 text-[10px] font-mono-tech uppercase tracking-wider text-zinc-400">
            <SlidersIcon className="w-3.5 h-3.5" />
            Zoom del recorte
          </label>
          <output htmlFor="brand-zoom" className="text-[11px] font-mono-tech font-bold text-[#E07A5F] tabular-nums">{percent}%</output>
        </div>
        <input
          id="brand-zoom"
          type="range"
          min={100}
          max={300}
          step={1}
          value={percent}
          disabled={!image}
          aria-describedby="brand-zoom-hint"
          onChange={(event) => onZoom(Number(event.target.value) / 100)}
          className="w-full h-1.5 rounded-full accent-[#E07A5F] bg-zinc-800 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#E07A5F]/70 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
        />
        <p id="brand-zoom-hint" className="text-[10px] text-zinc-500 leading-snug">
          Recorte <span className="text-zinc-300">cover</span> siempre centrado: el zoom amplía desde el centro, nunca recorta un borde.
        </p>
      </div>

      <fieldset className="space-y-2">
        <legend className="text-[10px] font-mono-tech uppercase tracking-wider text-zinc-400">Fondo del avatar y favicon</legend>
        <div className="grid grid-cols-2 gap-2">
          {AVATAR_BACKGROUNDS.map((option) => {
            const selected = option.id === background.id;
            return (
              <label
                key={option.id}
                className={`relative flex items-center gap-2 px-2.5 py-2 rounded-xl border cursor-pointer transition focus-within:ring-2 focus-within:ring-[#E07A5F]/70 ${
                  selected ? 'border-[#E07A5F]/60 bg-[#E07A5F]/[0.07]' : 'border-white/[0.08] bg-black/30 hover:border-white/20'
                }`}
              >
                <input
                  type="radio"
                  name="avatar-background"
                  value={option.id}
                  checked={selected}
                  onChange={() => onBackground(option)}
                  className="sr-only"
                />
                <span
                  aria-hidden="true"
                  className={`w-5 h-5 rounded-full border shrink-0 ${isImageBackgroundLight(option) ? 'border-black/25' : 'border-white/25'}`}
                  style={{ backgroundColor: option.hex }}
                />
                <span className={`text-[10px] font-mono-tech ${selected ? 'text-white' : 'text-zinc-400'}`}>{option.label}</span>
                <span className="ml-auto text-[9px] font-mono-tech text-zinc-500 tabular-nums">{option.hex}</span>
              </label>
            );
          })}
        </div>
      </fieldset>
    </section>
  );
};
