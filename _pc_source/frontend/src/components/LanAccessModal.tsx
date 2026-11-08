import React, { useEffect, useRef } from 'react';
import { copyText } from '../utils/clipboard';

interface Props {
  lanUrl: string;
  onClose: () => void;
}

export const LanAccessModal: React.FC<Props> = ({ lanUrl, onClose }) => {
  const closeRef = useRef<HTMLButtonElement | null>(null);
  const hasUrl = lanUrl.trim().length > 0;

  useEffect(() => {
    closeRef.current?.focus();
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4 font-ui"
      onClick={onClose}
      role="presentation"
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="lan-modal-title"
        className="bg-[#0e1017] border border-white/10 rounded-2xl max-w-md w-full p-5 space-y-3 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between gap-2">
          <span id="lan-modal-title" className="text-xs font-mono-tech uppercase text-emerald-400 font-bold tracking-wider">
            Acceso móvil LAN (Wi-Fi)
          </span>
          <button
            ref={closeRef}
            type="button"
            onClick={onClose}
            aria-label="Cerrar"
            className="text-zinc-400 hover:text-white text-xs font-mono-tech"
          >
            CERRAR
          </button>
        </div>
        {hasUrl ? (
          <>
            <p className="text-xs text-zinc-300 leading-relaxed">
              Servidor activo en <code className="text-emerald-300 font-mono-tech font-bold">0.0.0.0:8765</code>.
              Abre desde tu móvil conectado a la misma red:
            </p>
            <div className="p-3 rounded-xl bg-black/90 border border-emerald-500/30 font-mono-tech text-sm font-bold text-emerald-400 text-center select-all tabular-nums break-all">
              {lanUrl}
            </div>
            <button
              type="button"
              onClick={() => { void copyText(lanUrl); onClose(); }}
              className="w-full py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-mono-tech font-bold text-xs uppercase tracking-wider transition"
            >
              Copiar dirección LAN
            </button>
          </>
        ) : (
          <div className="space-y-2">
            <p className="text-xs text-zinc-300 leading-relaxed">
              No se detectó la IP de la LAN. El backend no ha informado <code className="text-zinc-100 font-mono-tech">lan_url</code> en
              <code className="text-zinc-100 font-mono-tech"> /api/health</code>, así que no se muestra una dirección inventada.
            </p>
            <p className="text-[11px] text-zinc-500 leading-relaxed">
              Revisa que el servidor escuche en 0.0.0.0:8765 y que el equipo esté conectado a la misma red que el móvil.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
