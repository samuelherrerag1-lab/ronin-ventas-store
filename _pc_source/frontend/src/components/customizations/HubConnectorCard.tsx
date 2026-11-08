import React from 'react';
import type { ConnectorCard } from '../../types/domain';
import type { ConnectJob } from '../../api/client';
import { ConnectorIcon } from './ConnectorLogos';
import { ChevronDown, ConnectIcon, PulseIcon, Spinner, StatusPill, cx } from './HubBits';
import {
  formatMs,
  formatTime,
  isBusyJob,
  jobLabel,
  shortName,
  statusTone,
  subtitle,
} from './connectorMeta';

interface HubConnectorCardProps {
  connector: ConnectorCard;
  job?: ConnectJob;
  expanded: boolean;
  onToggle: () => void;
  onConnect: (connectorId: string) => Promise<unknown> | void;
  onRunTest: (connectorId: string) => Promise<unknown> | void;
  testing: boolean;
}

const Meta: React.FC<{ label: string; value: string; mono?: boolean; title?: string }> = ({
  label,
  value,
  mono,
  title,
}) => (
  <div className="min-w-0">
    <dt className="text-[11px] leading-none text-zinc-400/80">{label}</dt>
    <dd
      title={title ?? value}
      className={cx(
        'mt-1.5 break-words text-[12px] leading-snug text-zinc-300',
        mono && 'break-all font-mono-tech text-[11px]',
      )}
    >
      {value}
    </dd>
  </div>
);

export const HubConnectorCard: React.FC<HubConnectorCardProps> = ({
  connector,
  job,
  expanded,
  onToggle,
  onConnect,
  onRunTest,
  testing,
}) => {
  const tone = statusTone(connector.status);
  const busy = isBusyJob(job?.status);
  const capabilities = connector.capabilities ?? [];
  const visibleCapabilities = capabilities.slice(0, 2);
  const extraCapabilities = capabilities.slice(2);
  const name = shortName(connector);

  return (
    <article
      id={`connector-card-${connector.connector_id}`}
      className={cx(
        'flex flex-col rounded-[18px] border bg-[#0f1014] p-5 transition-colors duration-150 ease-out',
        expanded
          ? 'border-white/[0.16]'
          : tone === 'fail'
            ? 'border-rose-400/20 hover:border-rose-400/35'
            : 'border-white/[0.07] hover:border-white/[0.13]',
      )}
    >
      <div className="flex items-start gap-3">
        <ConnectorIcon connectorId={connector.connector_id} />
        <div className="min-w-0 flex-1 pt-0.5">
          <h3 className="truncate font-grotesque text-[14px] font-semibold leading-tight text-white sm:text-[15px]">
            {name}
          </h3>
          <p className="mt-1.5 truncate text-[11px] text-zinc-400">{subtitle(connector)}</p>
        </div>
        <StatusPill tone={tone} />
      </div>

      <div className="mt-4 flex min-h-6 flex-wrap items-center gap-1.5">
        {busy ? (
          <div role="status" className="flex w-full items-center gap-2.5">
            <span className="relative flex h-4 w-4 shrink-0 items-center justify-center">
              <span className="absolute inset-0 rounded-full border-2 border-emerald-400/15" />
              <span className="absolute inset-0 animate-spin rounded-full border-2 border-transparent border-t-emerald-400" />
            </span>
            <span className="truncate text-[12px] text-zinc-300">{jobLabel(job?.status)}</span>
            {typeof job?.elapsed_sec === 'number' && (
              <span className="ml-auto shrink-0 font-mono-tech text-[11px] tabular-nums text-zinc-400/80">
                {job.elapsed_sec}s
              </span>
            )}
          </div>
        ) : (
          <>
            {visibleCapabilities.map((capability, index) => (
              <span
                key={capability}
                title={capability}
                className={cx(
                  'h-6 max-w-[190px] items-center truncate rounded-md border border-white/[0.06] bg-white/[0.03] px-2 text-[11px] leading-none text-zinc-400',
                  index === 1 ? 'hidden sm:inline-flex' : 'inline-flex',
                )}
              >
                {capability}
              </span>
            ))}
            {capabilities.length > 1 && (
              <span
                title={capabilities.slice(1).join(' · ')}
                className="inline-flex h-6 items-center rounded-md border border-white/[0.06] px-2 font-mono-tech text-[11px] leading-none text-zinc-400/80 sm:hidden"
              >
                +{capabilities.length - 1}
              </span>
            )}
            {extraCapabilities.length > 0 && (
              <span
                title={extraCapabilities.join(' · ')}
                className="hidden h-6 items-center rounded-md border border-white/[0.06] px-2 font-mono-tech text-[11px] leading-none text-zinc-400/80 sm:inline-flex"
              >
                +{extraCapabilities.length}
              </span>
            )}
            {capabilities.length === 0 && <span className="text-[11px] text-zinc-400">Sin capacidades declaradas</span>}
          </>
        )}
      </div>

      <div
        aria-hidden={!expanded}
        className={cx(
          'grid transition-[grid-template-rows,opacity] duration-200 ease-out',
          expanded ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0',
        )}
      >
        <div className="overflow-hidden">
          <div className="mt-4 space-y-3.5 border-t border-white/[0.06] pt-4">
            <p className="text-[12px] leading-relaxed text-zinc-400">{connector.description}</p>
            <dl className="grid grid-cols-1 gap-x-4 gap-y-3 sm:grid-cols-2">
              <Meta label="Método" value={connector.auth_mode} />
              <Meta label="Cuenta" value={connector.account_label} mono />
              <Meta label="Latencia" value={formatMs(connector.latency_ms)} mono />
              <Meta label="Última prueba" value={formatTime(connector.checked_at)} mono title={connector.checked_at} />
            </dl>
            {capabilities.length > 0 && (
              <p className="text-[11px] leading-relaxed text-zinc-400">
                <span className="text-zinc-400/80">Capacidades · </span>
                {capabilities.join(' · ')}
              </p>
            )}
            {connector.detail && (
              <p
                title={connector.detail}
                className={cx(
                  'line-clamp-3 font-mono-tech text-[11px] leading-relaxed',
                  tone === 'fail' ? 'text-rose-300/90' : 'text-zinc-400',
                )}
              >
                {connector.detail}
              </p>
            )}
          </div>
        </div>
      </div>

      <div className="mt-auto flex items-center gap-1.5 pt-4">
        <button
          type="button"
          onClick={() => onConnect(connector.connector_id)}
          disabled={busy}
          title={
            tone === 'ok'
              ? 'Volver a abrir Chrome y verificar la sesión'
              : 'Abrir Chrome, iniciar sesión y verificar la cuenta'
          }
          className={cx(
            'flex h-9 items-center gap-1.5 rounded-[10px] px-3 text-[12px] font-medium transition-colors duration-150 ease-out disabled:cursor-wait',
            busy
              ? 'border border-white/[0.06] bg-white/[0.04] text-zinc-400'
              : tone === 'ok'
                ? 'border border-white/[0.08] bg-white/[0.04] text-zinc-100 hover:bg-white/[0.08]'
                : 'bg-white text-[#0b0c0e] hover:bg-zinc-200',
          )}
        >
          {busy ? <Spinner className="h-3.5 w-3.5" /> : <ConnectIcon className="h-3.5 w-3.5" />}
          {busy ? 'Conectando' : tone === 'ok' ? 'Reconectar' : 'Conectar'}
        </button>

        <button
          type="button"
          onClick={() => onRunTest(connector.connector_id)}
          disabled={testing}
          title="Probar la conexión real"
          className="flex h-9 items-center gap-1.5 rounded-[10px] px-2.5 text-[12px] text-zinc-400 transition-colors duration-150 ease-out hover:bg-white/[0.05] hover:text-white disabled:opacity-60"
        >
          {testing ? <Spinner className="h-3.5 w-3.5" /> : <PulseIcon className="h-3.5 w-3.5" />}
          {testing ? 'Probando' : 'Probar'}
        </button>

        <button
          type="button"
          onClick={onToggle}
          aria-expanded={expanded}
          aria-label={expanded ? `Ocultar detalles de ${name}` : `Ver detalles de ${name}`}
          className="ml-auto flex h-8 w-8 items-center justify-center rounded-lg text-zinc-400 transition-colors duration-150 ease-out hover:bg-white/[0.05] hover:text-white"
        >
          <ChevronDown open={expanded} />
        </button>
      </div>
    </article>
  );
};
