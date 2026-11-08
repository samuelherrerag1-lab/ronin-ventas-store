/** Identity Studio: fuente a variantes de canvas y distribución. Todo en el navegador. */

import React, { useMemo, useState } from 'react';
import type { AvatarBackground, BrandCopy, ImageMeta, VariantSpec } from './brandSpecs';
import { AVATAR_BACKGROUNDS, BRAND, VARIANTS, slugify } from './brandSpecs';
import { downloadCanvas, loadImageFromFile, validateImageFile } from './imageIO';
import type { PaintOptions } from './painters';
import { paintVariant } from './painters';
import { BrandSourcePanel } from './BrandSourcePanel';
import { BrandIdentityPanel } from './BrandIdentityPanel';
import { PlatformApplyPanel } from './PlatformApplyPanel';
import { VariantCard } from './VariantCard';
import { CheckIcon, DownloadIcon, LockIcon } from './StudioIcons';

const DownloadAllButton: React.FC<{ disabled: boolean; busy: boolean; onClick: () => void }> = ({ disabled, busy, onClick }) => (
  <button
    type="button"
    onClick={onClick}
    disabled={disabled || busy}
    title={disabled ? 'Sube una imagen para habilitar las descargas' : 'Descarga las 5 variantes en PNG'}
    className="inline-flex items-center justify-center gap-2 px-3.5 py-2.5 rounded-xl bg-[#E07A5F] text-black text-[11px] font-mono-tech font-bold hover:bg-[#ea8b72] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#E07A5F] focus-visible:ring-offset-2 focus-visible:ring-offset-[#070A12] disabled:bg-white/[0.06] disabled:text-zinc-500 disabled:cursor-not-allowed transition"
  >
    <DownloadIcon className="w-3.5 h-3.5" />
    <span>{busy ? 'Generando PNG…' : 'Descargar todo (5 PNG)'}</span>
  </button>
);

export const IdentityStudioView: React.FC = () => {
  const [image, setImage] = useState<HTMLImageElement | null>(null);
  const [meta, setMeta] = useState<ImageMeta | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [decoding, setDecoding] = useState(false);
  const [zoom, setZoom] = useState(1);
  const [background, setBackground] = useState<AvatarBackground>(AVATAR_BACKGROUNDS[0]);
  const [brandName, setBrandName] = useState(BRAND.name);
  const [handle, setHandle] = useState(BRAND.handle);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  const copy = useMemo<BrandCopy>(
    () => ({ name: brandName, handle, tagline: BRAND.tagline }),
    [brandName, handle],
  );

  const paintOptions = useMemo<PaintOptions>(
    () => ({ zoom, background, copy }),
    [zoom, background, copy],
  );

  const handleFile = async (file: File) => {
    setNotice(null);
    const problem = validateImageFile(file);
    if (problem) {
      setError(problem);
      return;
    }
    setError(null);
    setDecoding(true);
    try {
      const loaded = await loadImageFromFile(file);
      setImage(loaded);
      setMeta({ name: file.name, size: file.size, width: loaded.naturalWidth, height: loaded.naturalHeight });
      setZoom(1);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'No se pudo cargar la imagen.');
    } finally {
      setDecoding(false);
    }
  };

  const handleClear = () => {
    setImage(null);
    setMeta(null);
    setError(null);
    setZoom(1);
    setNotice(null);
  };

  const downloadOne = async (spec: VariantSpec) => {
    if (!image) return;
    setBusy(true);
    try {
      const canvas = document.createElement('canvas');
      paintVariant(canvas, image, spec.id, paintOptions);
      const ok = await downloadCanvas(canvas, `${slugify(brandName)}-${spec.filename}`);
      setNotice(ok ? `PNG generado: ${spec.filename}` : 'El navegador bloqueó la descarga. Revisa los permisos del sitio.');
    } finally {
      setBusy(false);
    }
  };

  const downloadAll = async () => {
    if (!image) return;
    setBusy(true);
    let saved = 0;
    try {
      for (const spec of VARIANTS) {
        const canvas = document.createElement('canvas');
        paintVariant(canvas, image, spec.id, paintOptions);
        const ok = await downloadCanvas(canvas, `${slugify(brandName)}-${spec.filename}`);
        if (ok) saved += 1;
        await new Promise<void>((resolve) => {
          window.setTimeout(resolve, 220);
        });
      }
      setNotice(`${saved} de ${VARIANTS.length} variantes descargadas en PNG ${saved === VARIANTS.length ? '(completo)' : '(revisa el bloqueo de descargas)'}.`);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-4 text-zinc-100 font-ui">
      <header className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3 pb-4 border-b border-white/[0.08]">
        <div>
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <span className="px-2 py-0.5 rounded bg-[#E07A5F]/15 text-[#E07A5F] border border-[#E07A5F]/30 text-[10px] font-mono-tech uppercase tracking-wider font-bold">
              Brand OS · Identity Studio
            </span>
            <span className="flex items-center gap-1 text-[10px] font-mono-tech text-emerald-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" aria-hidden="true" />
              Canvas local · 0 bytes subidos
            </span>
          </div>
          <h1 className="text-xl font-bold tracking-tight text-white font-grotesque">Identity Studio</h1>
          <p className="text-xs text-zinc-400 mt-0.5">
            Una imagen, cinco variantes de marca recortadas en canvas y descargables como PNG real.
          </p>
        </div>
        <div className="flex flex-col items-stretch sm:items-end gap-1.5">
          <DownloadAllButton disabled={!image} busy={busy} onClick={downloadAll} />
          <span className="text-[10px] font-mono-tech text-zinc-500 flex items-center gap-1">
            <LockIcon className="w-3 h-3" />
            Procesado en el navegador, sin red.
          </span>
        </div>
      </header>

      {notice && (
        <div role="status" aria-live="polite" className="flex items-start justify-between gap-3 p-2.5 bg-[#090b10] border border-emerald-500/30 rounded-xl">
          <span className="text-[11px] font-mono-tech text-emerald-300 flex items-start gap-2 leading-snug">
            <CheckIcon className="w-3.5 h-3.5 shrink-0 mt-0.5" />
            {notice}
          </span>
          <button
            type="button"
            onClick={() => setNotice(null)}
            className="shrink-0 text-[10px] font-mono-tech text-zinc-500 hover:text-zinc-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-white/40 rounded px-1 transition"
          >
            Cerrar
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-4 items-start">
        <div className="xl:col-span-4">
          <BrandSourcePanel
            image={image}
            meta={meta}
            error={error}
            decoding={decoding}
            zoom={zoom}
            background={background}
            onFile={handleFile}
            onZoom={setZoom}
            onBackground={setBackground}
            onClear={handleClear}
          />
        </div>

        <div className="xl:col-span-8 space-y-3">
          <div className="flex flex-wrap items-end justify-between gap-2">
            <div>
              <p className="text-[10px] font-mono-tech font-bold uppercase tracking-wider text-[#E07A5F]">02 / Variantes</p>
              <h2 className="text-sm font-bold text-white font-grotesque">Generadas en canvas</h2>
            </div>
            <p className="text-[10px] font-mono-tech text-zinc-500 tabular-nums">
              {VARIANTS.length} formatos · PNG · {image ? 'listas' : 'esperando imagen'}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {VARIANTS.map((spec) => (
              <div key={spec.id} className="flex sm:last:col-span-2 sm:last:mx-auto sm:last:w-[calc(50%-0.375rem)]">
                <VariantCard
                  spec={spec}
                  image={image}
                  options={paintOptions}
                  copy={copy}
                  busy={busy}
                  onDownload={downloadOne}
                />
              </div>
            ))}
          </div>

          <p className="flex items-start gap-1.5 text-[10px] text-zinc-500 leading-snug">
            <LockIcon className="w-3.5 h-3.5 shrink-0 mt-0.5 text-zinc-600" />
            <span>El recorte es cover centrado con zoom sobre el centro. El PNG se renderiza de nuevo a tamaño final antes de descargar, no se escala la previsualización.</span>
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-4 items-start">
        <div className="xl:col-span-7">
          <PlatformApplyPanel />
        </div>
        <div className="xl:col-span-5">
          <BrandIdentityPanel
            name={brandName}
            handle={handle}
            onNameChange={setBrandName}
            onHandleChange={setHandle}
          />
        </div>
      </div>
    </div>
  );
};
