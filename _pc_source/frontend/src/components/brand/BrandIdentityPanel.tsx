/** Panel 04: identidad editable. El nombre y el handle se renderizan en las 5 variantes. */

import React, { useState } from 'react';
import { copyText } from '../../utils/clipboard';
import { CheckIcon, CopyIcon } from './StudioIcons';

interface BrandIdentityPanelProps {
  name: string;
  handle: string;
  onNameChange: (value: string) => void;
  onHandleChange: (value: string) => void;
}

const PALETTE = [
  { label: 'Terracota', hex: '#E07A5F', use: 'Acento y firma' },
  { label: 'Esmeralda', hex: '#10B981', use: 'Datos y verificación' },
  { label: 'Obsidiana', hex: '#08080C', use: 'Fondo del sistema' },
];

const TYPE_SAMPLES = [
  { family: 'Unbounded', role: 'Display · titulares', className: 'font-display' },
  { family: 'Bricolage Grotesque', role: 'Marca · títulos', className: 'font-grotesque' },
  { family: 'Geist', role: 'Interfaz · cuerpo', className: 'font-ui' },
  { family: 'Martian Mono', role: 'Datos · etiquetas', className: 'font-mono-tech' },
];

const fieldClass =
  'w-full mt-1 rounded-lg bg-black/50 border border-white/[0.1] px-2.5 py-1.5 text-xs text-white font-ui ' +
  'focus:outline-none focus-visible:ring-2 focus-visible:ring-[#E07A5F]/70 focus-visible:border-[#E07A5F]/50 transition';

export const BrandIdentityPanel: React.FC<BrandIdentityPanelProps> = ({ name, handle, onNameChange, onHandleChange }) => {
  const [copied, setCopied] = useState<string | null>(null);
  const [copyFailed, setCopyFailed] = useState(false);

  const copyHex = (hex: string) => {
    void copyText(hex).then((ok) => {
      setCopyFailed(!ok);
      if (!ok) return;
      setCopied(hex);
      window.setTimeout(() => setCopied((current) => (current === hex ? null : current)), 1600);
    });
  };

  return (
    <section aria-labelledby="identity-panel-title" className="bg-[#090b10] border border-white/[0.08] rounded-2xl p-4 space-y-4">
      <div>
        <p className="text-[10px] font-mono-tech font-bold uppercase tracking-wider text-[#E07A5F]">04 / Identidad</p>
        <h2 id="identity-panel-title" className="text-sm font-bold text-white font-grotesque mt-0.5">Marca y sistema visual</h2>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label htmlFor="brand-name" className="text-[10px] font-mono-tech uppercase tracking-wider text-zinc-400">Nombre de marca</label>
          <input
            id="brand-name"
            type="text"
            value={name}
            maxLength={34}
            onChange={(event) => onNameChange(event.target.value)}
            className={fieldClass}
            placeholder="Ron Overthinks"
          />
        </div>
        <div>
          <label htmlFor="brand-handle" className="text-[10px] font-mono-tech uppercase tracking-wider text-zinc-400">Handle</label>
          <input
            id="brand-handle"
            type="text"
            value={handle}
            maxLength={28}
            onChange={(event) => onHandleChange(event.target.value)}
            className={`${fieldClass} font-mono-tech`}
            placeholder="@ronoverthinks"
          />
        </div>
      </div>
      <p className="text-[10px] text-zinc-500 -mt-1">Ambos campos se pintan en las cinco variantes al instante.</p>

      <div className="space-y-2">
        <p className="text-[10px] font-mono-tech uppercase tracking-wider text-zinc-400">Paleta oficial</p>
        <div className="grid grid-cols-3 gap-2">
          {PALETTE.map((color) => {
            const isCopied = copied === color.hex;
            return (
              <button
                key={color.hex}
                type="button"
                onClick={() => copyHex(color.hex)}
                title={`Copiar ${color.hex}`}
                className="group text-left rounded-xl border border-white/[0.08] bg-black/40 p-2 hover:border-white/25 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#E07A5F]/70 transition"
              >
                <span
                  aria-hidden="true"
                  className="block h-9 w-full rounded-lg border border-white/10"
                  style={{ backgroundColor: color.hex }}
                />
                <span className="mt-1.5 flex items-center justify-between gap-1">
                  <span className="text-[10px] font-mono-tech text-zinc-200 tabular-nums">{color.hex}</span>
                  {isCopied
                    ? <CheckIcon className="w-3 h-3 text-emerald-400 shrink-0" />
                    : <CopyIcon className="w-3 h-3 text-zinc-600 group-hover:text-zinc-300 shrink-0" />}
                </span>
                <span className="block text-[9px] text-zinc-500 truncate mt-0.5">{color.label}</span>
              </button>
            );
          })}
        </div>
        <p aria-live="polite" className="text-[10px] font-mono-tech text-emerald-400 min-h-[14px]">
          {copyFailed ? 'No se pudo copiar (HTTP en LAN). Selecciona el texto manualmente.' : copied ? `${copied} copiado al portapapeles` : ''}
        </p>
      </div>

      <div className="space-y-2">
        <p className="text-[10px] font-mono-tech uppercase tracking-wider text-zinc-400">Tipografías del sistema</p>
        <ul className="divide-y divide-white/[0.06] border border-white/[0.06] rounded-xl overflow-hidden bg-black/30">
          {TYPE_SAMPLES.map((sample) => (
            <li key={sample.family} className="p-2.5 flex items-center justify-between gap-3">
              <div className="min-w-0">
                <p className="text-[11px] font-bold text-white truncate">{sample.family}</p>
                <p className="text-[9px] font-mono-tech text-zinc-500 mt-0.5">{sample.role}</p>
              </div>
              <span className={`${sample.className} text-lg text-zinc-200 shrink-0 leading-none`} aria-hidden="true">Aa 123</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
};
