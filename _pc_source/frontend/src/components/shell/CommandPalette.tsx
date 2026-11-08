import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Icon, type IconName } from '../ui/Icon';
import { NAV_ITEMS, type NavTabId } from './nav';

export interface PaletteAction {
  id: string;
  label: string;
  hint?: string;
  icon: IconName;
  run: () => void;
}

interface Props {
  open: boolean;
  onClose: () => void;
  onNavigate: (tab: NavTabId) => void;
  actions: PaletteAction[];
  demo: boolean;
}

interface Row {
  id: string;
  label: string;
  hint?: string;
  icon: IconName;
  group: 'Ir a' | 'Acciones';
  run: () => void;
}

const score = (text: string, query: string): number => {
  if (!query) return 1;
  const haystack = text.toLowerCase();
  const needle = query.toLowerCase();
  const direct = haystack.indexOf(needle);
  if (direct >= 0) return 100 - direct;
  let i = 0;
  for (const char of haystack) {
    if (char === needle[i]) i += 1;
    if (i === needle.length) return 10;
  }
  return 0;
};

/** Paleta de comandos Ctrl/Cmd+K: aparece sin animación (se usa decenas de veces al día). */
export const CommandPalette: React.FC<Props> = ({ open, onClose, onNavigate, actions, demo }) => {
  const [query, setQuery] = useState('');
  const [cursor, setCursor] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const rows = useMemo<Row[]>(
    () => [
      ...NAV_ITEMS.map((item) => ({
        id: `nav-${item.id}`,
        label: item.label,
        hint: item.group,
        icon: item.icon,
        group: 'Ir a' as const,
        run: () => onNavigate(item.id),
      })),
      ...actions.map((action) => ({ ...action, group: 'Acciones' as const })),
    ],
    [actions, onNavigate],
  );

  const results = useMemo(() => {
    if (!query) {
      const nav = rows.filter((row) => row.group === 'Ir a').slice(0, 6);
      const acts = rows.filter((row) => row.group === 'Acciones');
      return [...nav, ...acts];
    }
    return rows
      .map((row) => ({ row, s: score(`${row.label} ${row.hint ?? ''}`, query) }))
      .filter((entry) => entry.s > 0)
      .sort((a, b) => b.s - a.s)
      .slice(0, 9)
      .map((entry) => entry.row);
  }, [rows, query]);

  useEffect(() => {
    if (!open) return;
    setQuery('');
    setCursor(0);
    const t = window.setTimeout(() => inputRef.current?.focus(), 10);
    return () => window.clearTimeout(t);
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose();
      if (event.key === 'ArrowDown') {
        event.preventDefault();
        setCursor((c) => Math.min(results.length - 1, c + 1));
      }
      if (event.key === 'ArrowUp') {
        event.preventDefault();
        setCursor((c) => Math.max(0, c - 1));
      }
      if (event.key === 'Enter') {
        const picked = results[cursor];
        if (picked) {
          picked.run();
          onClose();
        }
      }
    };
    document.addEventListener('keydown', onKey, true);
    return () => document.removeEventListener('keydown', onKey, true);
  }, [open, results, cursor, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[70] flex items-start justify-center bg-black/60 p-3 pt-[12vh] sm:pt-[16vh]" role="presentation" onMouseDown={onClose}>
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Paleta de comandos"
        className="animate-fade w-full max-w-[580px] overflow-hidden rounded-xl border border-line2 bg-[#111114] shadow-[0_30px_80px_-20px_rgba(0,0,0,0.9)]"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="flex items-center gap-2.5 border-b border-line px-3.5">
          <Icon name="search" size={16} className="shrink-0 text-ink3" />
          <input
            ref={inputRef}
            value={query}
            onChange={(event) => {
              setQuery(event.target.value);
              setCursor(0);
            }}
            placeholder="Buscar módulo o ejecutar acción…"
            aria-label="Buscar módulo o acción"
            role="combobox"
            aria-expanded="true"
            aria-controls="palette-results"
            className="h-11 w-full bg-transparent text-[13.5px] text-ink outline-none placeholder:text-ink3"
          />
          {demo && <span className="chip border-transparent bg-warn/10 px-1.5 text-[10px] text-warn">demo</span>}
          <kbd className="rounded border border-line bg-panel2 px-1.5 py-0.5 text-[9.5px] text-ink3">esc</kbd>
        </div>

        <div id="palette-results" role="listbox" className="scroll-thin max-h-[52vh] p-1.5">
          {results.length === 0 && (
            <p className="px-3 py-6 text-center text-[12px] text-ink3">Nada coincide con “{query}”.</p>
          )}
          {results.map((row, index) => {
            const first = index === 0 || results[index - 1].group !== row.group;
            return (
              <React.Fragment key={row.id}>
                {first && <p className="px-2.5 pb-1 pt-2 text-[10px] text-ink3">{row.group}</p>}
                <button
                  type="button"
                  role="option"
                  aria-selected={cursor === index}
                  onMouseEnter={() => setCursor(index)}
                  onClick={() => {
                    row.run();
                    onClose();
                  }}
                  className={`flex w-full items-center gap-2.5 rounded-ctl px-2.5 py-2 text-left text-[12.5px] transition-colors duration-100 ${
                    cursor === index ? 'bg-panel2 text-ink' : 'text-ink2'
                  }`}
                >
                  <Icon name={row.icon} size={15} className={cursor === index ? 'text-accent' : 'text-ink3'} />
                  <span className="flex-1 truncate">{row.label}</span>
                  {row.hint && <span className="text-[10.5px] text-ink3">{row.hint}</span>}
                  {cursor === index && <Icon name="arrow-right" size={12} className="text-ink3" />}
                </button>
              </React.Fragment>
            );
          })}
        </div>

        <div className="flex items-center gap-3 border-t border-line px-3.5 py-1.5 text-[10px] text-ink3">
          <span className="flex items-center gap-1"><kbd className="rounded border border-line px-1">↑↓</kbd> mover</span>
          <span className="flex items-center gap-1"><kbd className="rounded border border-line px-1">↵</kbd> abrir</span>
          <span className="ml-auto">{results.length} resultados</span>
        </div>
      </div>
    </div>
  );
};
