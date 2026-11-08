import React from 'react';
import type { StealthDiagnostic } from '../../types/domain';

/** Panel forense del Chrome Vault. Solo muestra hechos medidos. */
export const StealthForensicsPanel: React.FC<{ diagnostic?: StealthDiagnostic }> = ({ diagnostic }) => {
  const facts = [
    { label: 'Binario Chrome', ok: diagnostic?.chrome_binary_found, detail: diagnostic?.chrome_binary_path || 'No encontrado' },
    { label: 'Perfil persistente', ok: diagnostic?.profile_exists, detail: diagnostic?.persistent_vault_dir || '---' },
    { label: 'Cookies legibles', ok: diagnostic?.cookies_readable, detail: diagnostic?.cookies_reason || `${diagnostic?.domains_with_cookies?.length ?? 0} dominios` },
    { label: 'Playwright', ok: diagnostic?.playwright_installed, detail: diagnostic?.playwright_installed ? 'Instalado' : 'No instalado' },
  ];
  const domains = diagnostic?.domains_with_cookies?.length ? diagnostic.domains_with_cookies : ['ninguno'];

  return (
    <div className="p-4 bg-[#090b10] border border-white/[0.08] rounded-2xl space-y-3">
      <div className="flex items-center justify-between border-b border-white/[0.06] pb-2">
        <div>
          <span className="text-xs font-bold uppercase font-mono-tech text-emerald-400">Expediente Forense Anti-Bot</span>
          <p className="text-[11px] text-zinc-400">Solo hechos medidos del Chrome Vault. Sin puntuaciones estimadas.</p>
        </div>
        <div className="text-right">
          <span className="text-2xl font-black text-zinc-500 font-display tabular-nums">N/D</span>
          <span className="text-[10px] text-zinc-500 block font-mono-tech">FINGERPRINT NO MEDIDO</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3 text-xs">
        {facts.map((f) => (
          <div key={f.label} className="bg-black/60 p-2.5 rounded-xl border border-white/[0.05] space-y-1">
            <div className="flex justify-between gap-2 text-[11px] font-mono-tech">
              <span className="text-zinc-400">{f.label}:</span>
              <span className={f.ok ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}>{f.ok ? 'OK' : 'NO'}</span>
            </div>
            <p className="text-[10px] text-zinc-500 font-mono-tech break-all leading-tight">{f.detail}</p>
          </div>
        ))}
      </div>

      <div className="bg-black/60 p-2.5 rounded-xl border border-white/[0.05]">
        <div className="flex items-center justify-between text-[11px] font-mono-tech mb-1.5">
          <span className="text-zinc-400">Dominios con cookies en el vault:</span>
          <span className="text-zinc-300 tabular-nums">
            {diagnostic?.domains_with_cookies?.length ?? 0} · {diagnostic?.session_cookie_count ?? 0} de sesión
          </span>
        </div>
        <div className="flex flex-wrap gap-1">
          {domains.map((d) => (
            <span
              key={d}
              className={`text-[9px] px-1.5 py-0.5 rounded border font-mono-tech ${
                d === 'ninguno' ? 'border-zinc-800 text-zinc-600' : 'border-emerald-500/30 text-emerald-300 bg-emerald-500/5'
              }`}
            >
              {d}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};
