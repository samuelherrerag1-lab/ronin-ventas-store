/** Tarjeta de una variante: canvas real + descarga PNG individual. */

import React, { useEffect, useRef } from 'react';
import type { BrandCopy, VariantSpec } from './brandSpecs';
import { paintVariant } from './painters';
import type { PaintOptions } from './painters';
import { DownloadIcon, ImageIcon } from './StudioIcons';

interface VariantCardProps {
  spec: VariantSpec;
  image: HTMLImageElement | null;
  options: PaintOptions;
  copy: BrandCopy;
  busy: boolean;
  onDownload: (spec: VariantSpec) => void;
}

export const VariantCard: React.FC<VariantCardProps> = ({ spec, image, options, copy, busy, onDownload }) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const compact = spec.id === 'favicon';

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return undefined;
    let alive = true;

    paintVariant(canvas, image, spec.id, options);

    // Las fuentes variables pueden terminar de cargar después del primer pintado.
    if (typeof document !== 'undefined' && document.fonts && document.fonts.ready) {
      document.fonts.ready
        .then(() => {
          if (alive && canvasRef.current) paintVariant(canvasRef.current, image, spec.id, options);
        })
        .catch(() => undefined);
    }

    return () => {
      alive = false;
    };
  }, [image, options, spec.id]);

  const ready = Boolean(image);

  return (
    <figure className={`w-full bg-[#090b10] border border-white/[0.08] rounded-2xl overflow-hidden hover:border-[#E07A5F]/35 transition-colors ${
      compact ? 'flex flex-row items-stretch' : 'flex flex-col'
    }`}>
      <div className={`relative flex items-center justify-center bg-black/50 ${
        compact ? 'p-4 shrink-0 border-r border-white/[0.06]' : 'h-[230px] p-3'
      }`}>
        <canvas
          ref={canvasRef}
          role="img"
          aria-label={`${spec.label} de ${copy.name || 'la marca'}, ${spec.detail} píxeles`}
          className={compact ? 'w-16 h-16' : 'max-h-full max-w-full object-contain'}
          style={compact ? { imageRendering: 'pixelated' } : undefined}
        >
          {spec.label} — {spec.detail}
        </canvas>
        {!ready && !compact && (
          <span className="absolute bottom-2 left-2 text-[9px] font-mono-tech px-1.5 py-0.5 rounded bg-black/80 border border-white/10 text-zinc-400">
            Vista previa sin imagen
          </span>
        )}
      </div>

      <figcaption className={`p-3 flex items-start justify-between gap-2 ${
        compact ? 'flex-1 border-l border-white/[0.06]' : 'border-t border-white/[0.06] mt-auto'
      }`}>
        <div className="min-w-0">
          <div className="flex items-center gap-1.5">
            <ImageIcon className="w-3.5 h-3.5 text-[#E07A5F] shrink-0" />
            <p className="text-[11px] font-bold text-white font-grotesque truncate">{spec.label}</p>
          </div>
          <p className="text-[9px] font-mono-tech text-zinc-500 mt-1 tabular-nums">{spec.detail} px</p>
          <p className="text-[10px] text-zinc-500 mt-0.5 leading-snug">{spec.use}</p>
        </div>
        <button
          type="button"
          onClick={() => onDownload(spec)}
          disabled={!ready || busy}
          title={ready ? `Descargar ${spec.filename}` : 'Sube una imagen para descargar'}
          className="shrink-0 inline-flex items-center gap-1 px-2 py-1.5 rounded-lg border border-white/10 bg-white/[0.04] text-[10px] font-mono-tech font-bold text-zinc-200 hover:border-[#E07A5F]/50 hover:text-[#E07A5F] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#E07A5F]/70 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:text-zinc-200 disabled:hover:border-white/10 transition"
          aria-label={`Descargar ${spec.label} en PNG`}
        >
          <DownloadIcon className="w-3.5 h-3.5" />
          <span>PNG</span>
        </button>
      </figcaption>
    </figure>
  );
};
