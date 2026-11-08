import React, { useEffect, useState } from 'react';
import { fetchCustomizations, testAllConnectors, testConnector } from '../../api/client';
import type { ConnectorCard, CustomizationsOverview } from '../../types/domain';
import { HubConnectorDeck } from './HubConnectorDeck';
import { HubDiagnosticTerminal, type TerminalLogEntry } from './HubDiagnosticTerminal';
import { HubHeader, type HubTab } from './HubHeader';
import { HubSkillsTable } from './HubSkillsTable';
import { useConnectorJobs } from './useConnectorJobs';

export interface CustomizationsHubViewProps {
  overview?: CustomizationsOverview | null;
  onConnect: (connectorId: string) => Promise<unknown> | void;
  onToggleSkill: (skillId: string, enabled: boolean) => Promise<unknown> | void;
}

export const CustomizationsHubView: React.FC<CustomizationsHubViewProps> = ({
  overview,
  onConnect,
  onToggleSkill,
}) => {
  const [activeTab, setActiveTab] = useState<HubTab>('connectors');
  const [testingId, setTestingId] = useState<string | null>(null);
  const [isRunningAll, setIsRunningAll] = useState(false);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [logs, setLogs] = useState<TerminalLogEntry[]>([]);
  const [terminalOpen, setTerminalOpen] = useState(false);
  const [localData, setLocalData] = useState<CustomizationsOverview | null>(overview || null);

  const connectors = localData?.connectors || overview?.connectors || [];
  const skills = localData?.skills || overview?.skills || [];
  const connectedCount = connectors.filter((c) => c.status === 'CONECTADO').length;
  const failCount = connectors.filter((c) => c.status === 'FALLA').length;

  const appendLog = (entry: Omit<TerminalLogEntry, 'id' | 'timestamp'>) => {
    const newEntry: TerminalLogEntry = {
      ...entry,
      id: Math.random().toString(36).substring(2, 9),
      timestamp: new Date().toLocaleTimeString('es-CO', { hour12: false }),
    };
    if (entry.level === 'error') setTerminalOpen(true);
    setLogs((prev) => [...prev.slice(-80), newEntry]);
  };

  /** Aplica el resultado de una prueba sin mutar el estado de React. */
  const patchConnector = (connectorId: string, patch: Partial<ConnectorCard>) => {
    setLocalData((prev) =>
      prev
        ? {
            ...prev,
            connectors: prev.connectors.map((c) =>
              c.connector_id === connectorId ? { ...c, ...patch } : c
            ),
          }
        : prev
    );
  };

  const handleRunSingleTest = async (connectorId: string) => {
    setTestingId(connectorId);
    appendLog({ level: 'info', tag: connectorId.toUpperCase(), message: `Lanzando prueba real...` });
    try {
      const res = await testConnector(connectorId);
      const isOk = res.status === 'CONECTADO';
      const isFail = res.status === 'FALLA';
      appendLog({
        level: isOk ? 'success' : isFail ? 'error' : 'warn',
        tag: res.status,
        message: res.detail || `${connectorId}: ${res.status}`,
        latency_ms: res.latency_ms,
      });
      const target = connectors.find((c) => c.connector_id === connectorId);
      if (target) {
        patchConnector(connectorId, {
          status: res.status,
          latency_ms: res.latency_ms,
          detail: res.detail,
          checked_at: res.checked_at,
        });
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      appendLog({ level: 'error', tag: 'ERROR', message: `Excepción: ${msg}` });
    } finally {
      const updated = await fetchCustomizations().catch(() => null);
      if (updated) setLocalData(updated);
      setTestingId(null);
    }
  };

  const { jobs, startPolling } = useConnectorJobs((job) => {
    if (job.status === 'connected') {
      appendLog({ level: 'success', tag: 'CONECTADO', message: job.evidence || job.detail || job.step || 'Conexión verificada.' });
      fetchCustomizations().then(setLocalData).catch(() => {});
      handleRunSingleTest(job.connector_id);
    } else {
      appendLog({
        level: 'error',
        tag: job.status.toUpperCase(),
        message: job.detail || job.step || 'Sin detalle del trabajador.',
      });
    }
  });

  useEffect(() => {
    if (overview) setLocalData(overview);
    else fetchCustomizations().then(setLocalData).catch(() => {});
  }, [overview]);

  const handleRunAll = async () => {
    if (isRunningAll) return;
    setIsRunningAll(true);
    setTerminalOpen(true);
    appendLog({ level: 'info', tag: 'INIT', message: 'Iniciando diagnóstico real completo en paralelo...' });
    try {
      const res = await testAllConnectors();
      appendLog({
        level: res.falla_count > 0 ? 'error' : 'success',
        tag: 'SUMMARY',
        message: `Diagnóstico finalizado: ${res.connected_count} Conectados, ${res.falla_count} Fallas, ${res.sin_verificar_count} Sin Verificar`,
      });
      Object.entries(res.results).forEach(([cid, item]) => {
        const isOk = item.status === 'CONECTADO';
        const isFail = item.status === 'FALLA';
        appendLog({
          level: isOk ? 'success' : isFail ? 'error' : 'warn',
          tag: item.status,
          message: `${item.name}: ${item.detail}`,
          latency_ms: item.latency_ms,
        });
        const target = connectors.find((c) => c.connector_id === cid);
        if (target) {
          patchConnector(cid, {
            status: item.status,
            latency_ms: item.latency_ms,
            detail: item.detail,
            checked_at: item.checked_at,
          });
        }
      });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      appendLog({ level: 'error', tag: 'FATAL', message: `Falla en test-all: ${msg}` });
    } finally {
      const updated = await fetchCustomizations().catch(() => null);
      if (updated) setLocalData(updated);
      setIsRunningAll(false);
    }
  };

  const handleConnectClick = async (connectorId: string) => {
    appendLog({ level: 'info', tag: 'LOGIN', message: `Abriendo ${connectorId} con el perfil persistente...` });
    try {
      const res = (await onConnect(connectorId)) as { status?: string; detail?: string } | undefined;
      const status = res?.status ?? 'sin_respuesta';
      if (status === 'manual_required') {
        appendLog({ level: 'warn', tag: 'MANUAL', message: res?.detail || 'Este conector no usa navegador.' });
        return;
      }
      appendLog({
        level: 'info',
        tag: 'LOGIN',
        message: res?.detail || 'Chrome abierto. Inicia sesión en la ventana y el sistema detectará la sesión.',
      });
      startPolling(connectorId);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      appendLog({ level: 'error', tag: 'LOGIN', message: `Excepción: ${msg}` });
    }
  };

  const handleToggle = async (skillId: string, current: boolean) => {
    setBusyId(skillId);
    try {
      await onToggleSkill(skillId, !current);
    } finally {
      setBusyId(null);
    }
  };

  return (
    <div className="mx-auto w-full max-w-[1120px] py-2 font-ui text-zinc-100 [&_button:focus-visible]:outline [&_button:focus-visible]:outline-2 [&_button:focus-visible]:outline-offset-2 [&_button:focus-visible]:outline-white/50 sm:py-4">
      <HubHeader
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        connectorsCount={connectors.length}
        skillsCount={skills.length}
        connectedCount={connectedCount}
        failCount={failCount}
        isRunningAll={isRunningAll}
        onRunAll={handleRunAll}
        finopsSpent={localData?.finops?.total_spent_usd ?? 0}
        finopsLimit={localData?.finops?.circuit_breaker_limit_usd ?? 0}
        ledgerFound={localData?.finops?.ledger_found ?? false}
        projectId={localData?.finops?.project_id ?? null}
      />

      {activeTab === 'connectors' ? (
        <div className="mt-5 space-y-4">
          <HubDiagnosticTerminal
            logs={logs}
            onClear={() => setLogs([])}
            isRunningAll={isRunningAll}
            open={terminalOpen}
            onToggle={() => setTerminalOpen((open) => !open)}
          />
          <HubConnectorDeck
            connectors={connectors}
            jobs={jobs}
            onConnect={handleConnectClick}
            onRunTest={handleRunSingleTest}
            testingId={testingId}
          />
        </div>
      ) : (
        <div className="mt-5">
          <HubSkillsTable skills={skills} onToggleSkill={handleToggle} busyId={busyId} />
        </div>
      )}
    </div>
  );
};
