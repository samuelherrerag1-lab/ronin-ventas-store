import React, { useEffect, useRef } from 'react';
import { ChevronDown, Spinner, TerminalIcon } from './HubBits';

export interface TerminalLogEntry {
  id: string;
  timestamp: string;
  level: 'info' | 'success' | 'warn' | 'error';
  tag: string;
  message: string;
  latency_ms?: number;
}

interface HubDiagnosticTerminalProps {
  logs: TerminalLogEntry[];
  onClear: () => void;
  isRunningAll: boolean;
  open: boolean;
  onToggle: () => void;
}

const LEVEL_CLASS: Record<TerminalLogEntry['level'], string> = {
  info: 'text-zinc-400',
  success: 'text-emerald-400',
  warn: 'text-amber-300',
  error: 'text-rose-400',
};

export const HubDiagnosticTerminal: React.FC<HubDiagnosticTerminalProps> = ({
  logs,
  onClear,
  isRunningAll,
  open,
  onToggle,
}) => {
  const endRef = useRef<HTMLDivElement>(null);
  const errorCount = logs.filter((log) => log.level === 'error').length;

  useEffect(() => {
    if (open) endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }, [logs, open]);

  return (
    <section className="overflow-hidden rounded-2xl border border-white/[0.07] bg-[#0c0d10]">
      <div className="flex h-12 items-center gap-2 px-4">
        <button
          type="button"
          onClick={onToggle}
          aria-expanded={open}
          aria-controls="hub-diagnostic-log"
          className="flex min-w-0 flex-1 items-center gap-2.5 text-left"
        >
          <TerminalIcon className="h-4 w-4 shrink-0 text-zinc-400" />
          <span className="text-[12px] text-zinc-300">Diagnóstico</span>
          {logs.length > 0 && (
            <span className="font-mono-tech text-[11px] tabular-nums text-zinc-400/80">{logs.length}</span>
          )}
          {errorCount > 0 && <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-rose-400" aria-hidden="true" />}
          {isRunningAll && <Spinner className="h-3.5 w-3.5 shrink-0 text-emerald-400" />}
          <span className="ml-auto flex items-center gap-2">
            {logs.length === 0 && !isRunningAll && (
              <span className="text-[11px] text-zinc-400/80">Sin eventos</span>
            )}
            <ChevronDown open={open} className="h-4 w-4 shrink-0 text-zinc-400" />
          </span>
          <span className="sr-only">{open ? 'Ocultar diagnóstico' : 'Mostrar diagnóstico'}</span>        </button>
        {open && logs.length > 0 && (
          <button
            type="button"
            onClick={onClear}
            className="ml-3 shrink-0 text-[11px] text-zinc-400 transition-colors duration-150 hover:text-zinc-100"
          >
            Limpiar
          </button>
        )}
      </div>

      {open && (
        <div id="hub-diagnostic-log" className="max-h-56 overflow-y-auto border-t border-white/[0.06] px-4 py-3">
          {logs.length === 0 ? (
            <p className="py-2 font-mono-tech text-[11px] text-zinc-400">
              Sin eventos. Ejecuta un diagnóstico para ver la traza.
            </p>
          ) : (
            <div className="space-y-1">
              {logs.map((log) => (
                <div
                  key={log.id}
                  className="flex flex-wrap items-start gap-x-2.5 gap-y-0.5 rounded px-1 py-1 font-mono-tech text-[11px] leading-relaxed hover:bg-white/[0.02] sm:flex-nowrap"
                >
                  <span className="hidden w-[62px] shrink-0 text-zinc-400/80 sm:block">{log.timestamp}</span>
                  <span className={`order-1 w-auto shrink-0 font-semibold sm:order-2 sm:w-[120px] sm:truncate ${LEVEL_CLASS[log.level]}`}>
                    {log.tag}
                  </span>
                  <span className={`order-3 w-full min-w-0 break-words sm:order-3 sm:w-auto sm:flex-1 ${log.level === 'error' ? 'text-rose-200/90' : 'text-zinc-300'}`}>
                    {log.message}
                  </span>
                  {log.latency_ms !== undefined && (
                    <span className="order-2 ml-auto shrink-0 tabular-nums text-zinc-400/80 sm:order-4 sm:ml-0">{Math.round(log.latency_ms)}ms</span>
                  )}
                </div>
              ))}
            </div>
          )}
          <div ref={endRef} />
        </div>
      )}
    </section>
  );
};
