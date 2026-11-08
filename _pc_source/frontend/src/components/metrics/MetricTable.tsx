import React, { useMemo, useState } from 'react';
import { Icon } from '../ui/Icon';
import { Panel, PanelHead } from '../ui/primitives';
import { num, pct, ratio } from '../../utils/format';
import type { PieceRow } from './metricsModel';

type SortKey = 'piece_id' | 'platform' | 'impressions' | 'clicks' | 'ctr' | 'saves' | 'verdict';

const VERDICT_STYLE: Record<string, string> = {
  DOBLAR: 'text-pos border-pos/30 bg-pos/10',
  MATAR: 'text-neg border-neg/30 bg-neg/10',
  MUTAR: 'text-warn border-warn/30 bg-warn/10',
  OBSERVACION: 'text-ink2 border-line bg-panel3',
};

const COLUMNS: { key: SortKey; label: string; numeric?: boolean }[] = [
  { key: 'piece_id', label: 'Pieza' },
  { key: 'platform', label: 'Canal' },
  { key: 'impressions', label: 'Impresiones', numeric: true },
  { key: 'clicks', label: 'Clics', numeric: true },
  { key: 'ctr', label: 'CTR', numeric: true },
  { key: 'saves', label: 'Saves', numeric: true },
  { key: 'verdict', label: 'Veredicto' },
];

/** Tabla de piezas ordenable por cualquier columna; cifras tabulares a la derecha. */
export const MetricTable: React.FC<{ rows: PieceRow[] }> = ({ rows }) => {
  const [sort, setSort] = useState<{ key: SortKey; dir: 'asc' | 'desc' }>({ key: 'impressions', dir: 'desc' });

  const sorted = useMemo(() => {
    const data = [...rows];
    data.sort((a, b) => {
      const key = sort.key;
      const av = a[key] ?? '';
      const bv = b[key] ?? '';
      const cmp = typeof av === 'number' && typeof bv === 'number' ? av - bv : String(av).localeCompare(String(bv));
      return sort.dir === 'asc' ? cmp : -cmp;
    });
    return data;
  }, [rows, sort]);

  const toggle = (key: SortKey) =>
    setSort((current) => (current.key === key ? { key, dir: current.dir === 'asc' ? 'desc' : 'asc' } : { key, dir: 'desc' }));

  return (
    <Panel className="flex flex-col">
      <PanelHead
        title="Piezas medidas"
        icon="list"
        hint={`${rows.length} registradas`}
        actions={
          <span className="chip hidden border-transparent bg-panel3 px-1.5 sm:inline-flex">
            orden: {sort.key === 'ctr' ? 'CTR' : sort.key === 'clicks' ? 'clics' : 'impresiones'} · {sort.dir === 'desc' ? '↓' : '↑'}
          </span>
        }
      />
      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] border-collapse text-[11.5px]">
          <thead>
            <tr className="border-b border-line">
              {COLUMNS.map((col) => {
                const active = sort.key === col.key;
                return (
                  <th
                    key={col.key}
                    scope="col"
                    aria-sort={active ? (sort.dir === 'asc' ? 'ascending' : 'descending') : 'none'}
                    className={`h-9 whitespace-nowrap px-3 text-[10.5px] font-normal text-ink3 ${col.numeric ? 'text-right' : 'text-left'}`}
                  >
                    <button
                      type="button"
                      onClick={() => toggle(col.key)}
                      className={`inline-flex items-center gap-1 transition-colors duration-150 hover:text-ink ${active ? 'text-ink2' : ''}`}
                    >
                      {col.label}
                      <Icon name="sort" size={10} className={active ? 'text-accent' : 'text-ink3/50'} />
                    </button>
                  </th>
                );
              })}
              <th scope="col" className="h-9 px-3 text-left text-[10.5px] font-normal text-ink3">Ruta</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {sorted.length === 0 && (
              <tr>
                <td colSpan={8} className="px-3 py-8 text-center text-[11.5px] text-ink3">
                  Sin piezas registradas. La tabla conserva su marco para que el hueco se note.
                </td>
              </tr>
            )}
            {sorted.map((row) => (
              <tr key={`${row.platform}-${row.piece_id}`} className="transition-colors duration-150 hover:bg-panel2/60">
                <td className="h-10 px-3">
                  <span className="mono-id text-ink2">{row.piece_id}</span>
                  {row.sku_id && <span className="ml-2 text-[10px] text-ink3">{row.sku_id}</span>}
                </td>
                <td className="px-3 text-ink2">{row.platform === 'pinterest' ? 'Pinterest' : 'Threads'}</td>
                <td className="num px-3 text-right text-ink2">{num(row.impressions)}</td>
                <td className="num px-3 text-right text-ink2">{num(row.clicks)}</td>
                <td className="px-3">
                  <span className="flex items-center justify-end gap-2">
                    <span className="hidden h-[3px] w-12 overflow-hidden rounded-full bg-[#16161b] sm:block">
                      <span className="block h-full rounded-full bg-accent/70" style={{ width: `${Math.max(2, ratio(row.ctr, 3) * 100)}%` }} />
                    </span>
                    <span className="num text-ink">{pct(row.ctr, 2)}</span>
                  </span>
                </td>
                <td className="num px-3 text-right text-ink2">{num(row.saves)}</td>
                <td className="px-3">
                  <span className={`chip border px-1.5 text-[9.5px] ${VERDICT_STYLE[row.verdict] ?? VERDICT_STYLE.OBSERVACION}`}>
                    {row.verdict}
                  </span>
                </td>
                <td className="max-w-[180px] px-3">
                  <span className="mono-id block truncate text-ink3">{row.route ?? '—'}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Panel>
  );
};
