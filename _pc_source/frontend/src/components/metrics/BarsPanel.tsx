import React from 'react';
import { Icon } from '../ui/Icon';
import { Panel, PanelHead } from '../ui/primitives';
import { Tip } from '../ui/Tooltip';
import { num, pct, ratio } from '../../utils/format';
import type { PieceRow } from './metricsModel';

export type BarMetric = 'impressions' | 'clicks' | 'saves';

interface Props {
  rows: PieceRow[];
  metric: BarMetric;
  onMetric: (metric: BarMetric) => void;
}

const TONE: Record<string, string> = {
  DOBLAR: 'bg-pos/80',
  MATAR: 'bg-neg/80',
  MUTAR: 'bg-warn/80',
  OBSERVACION: 'bg-[#4b4b58]',
};

/** Ranking de piezas con la barra como dato; el color dice el veredicto, no la magnitud. */
export const BarsPanel: React.FC<Props> = ({ rows, metric, onMetric }) => {
  const max = Math.max(1, ...rows.map((row) => row[metric]));
  const top = rows.slice(0, 6);
  const channels = (['threads', 'pinterest'] as const).map((platform) => ({
    id: platform,
    label: platform === 'threads' ? 'Threads' : 'Pinterest',
    value: rows.filter((row) => row.platform === platform).reduce((sum, row) => sum + row[metric], 0),
  }));
  const channelMax = Math.max(1, ...channels.map((channel) => channel.value));

  return (
    <Panel className="flex h-full flex-col">
      <PanelHead
        title="Piezas"
        icon="chart"
        actions={
          <div className="seg" role="group" aria-label="Métrica del ranking">
            {(['impressions', 'clicks', 'saves'] as BarMetric[]).map((key) => (
              <button key={key} type="button" aria-pressed={metric === key} onClick={() => onMetric(key)}>
                {key === 'impressions' ? 'Impr.' : key === 'clicks' ? 'Clics' : 'Saves'}
              </button>
            ))}
          </div>
        }
      />
      <div className="flex flex-1 flex-col p-2">
        {top.length === 0 ? (
          <div className="flex min-h-[150px] flex-1 flex-col items-center justify-center gap-2 px-4 text-center">
            <Icon name="chart" size={17} className="text-ink3" />
            <p className="text-[12px] text-ink">Sin piezas medidas</p>
            <p className="max-w-[34ch] text-[10.5px] leading-relaxed text-ink3">
              Registra impresiones y clics por pieza para ver el ranking.
            </p>
          </div>
        ) : (
          <>
            <ul className="space-y-1">
              {top.map((row) => (
                <li key={`${row.platform}-${row.piece_id}`}>
                  <Tip
                    side="top"
                    label={
                      <span className="block">
                        <b className="block text-ink">{row.piece_id}</b>
                        <span className="text-ink2">
                          {num(row.impressions)} impr · {num(row.clicks)} clics · {pct(row.ctr, 2)} CTR
                        </span>
                        {row.route && <span className="mt-0.5 block text-ink3">{row.route}</span>}
                      </span>
                    }
                  >
                    <div className="rounded-ctl px-2 py-1.5 transition-colors duration-150 hover:bg-panel2/70">
                      <div className="flex items-baseline justify-between gap-2">
                        <span className="mono-id truncate text-ink2">{row.piece_id}</span>
                        <span className="num shrink-0 text-[11.5px] text-ink">{num(row[metric])}</span>
                      </div>
                      <div className="mt-1 flex items-center gap-2">
                        <span className="h-[4px] flex-1 overflow-hidden rounded-full bg-[#16161b]">
                          <span
                            className={`block h-full rounded-full ${TONE[row.verdict] ?? TONE.OBSERVACION}`}
                            style={{ width: `${Math.max(2, ratio(row[metric], max) * 100)}%` }}
                          />
                        </span>
                        <span className="w-9 shrink-0 text-right text-[9.5px] text-ink3">{row.platform === 'pinterest' ? 'pin' : 'th'}</span>
                      </div>
                    </div>
                  </Tip>
                </li>
              ))}
            </ul>
            <div className="mt-auto border-t border-line pt-2">
              <p className="mb-1.5 px-2 text-[9.5px] text-ink3">Por canal</p>
              {channels.map((channel) => (
                <div key={channel.id} className="mb-1 flex items-center gap-2 px-2 last:mb-0">
                  <span className="w-[56px] shrink-0 text-[10px] text-ink3">{channel.label}</span>
                  <span className="h-[3px] flex-1 overflow-hidden rounded-full bg-[#16161b]">
                    <span
                      className="block h-full rounded-full bg-ink3/60"
                      style={{ width: `${Math.max(2, ratio(channel.value, channelMax) * 100)}%` }}
                    />
                  </span>
                  <span className="num w-10 shrink-0 text-right text-[10px] text-ink2">{num(channel.value)}</span>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
      <footer className="flex items-center justify-between border-t border-line px-4 py-2 text-[10px] text-ink3">
        <span className="flex items-center gap-3">
          <span className="flex items-center gap-1"><span className="dot bg-pos/80" />Doblar</span>
          <span className="flex items-center gap-1"><span className="dot bg-warn/80" />Mutar</span>
          <span className="flex items-center gap-1"><span className="dot bg-neg/80" />Matar</span>
        </span>
        <span>{rows.length} piezas</span>
      </footer>
    </Panel>
  );
};
