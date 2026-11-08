import { useCallback, useEffect, useRef, useState } from 'react';
import { fetchConnectStatus, type ConnectJob } from '../../api/client';

const TERMINAL = new Set([
  'connected',
  'logged_in_no_token',
  'failed',
  'timeout',
  'stopped',
]);

export interface UseConnectorJobsResult {
  jobs: Record<string, ConnectJob>;
  startPolling: (connectorId: string) => void;
  clearJob: (connectorId: string) => void;
}

/**
 * Consulta el estado real del trabajador de conexión cada 2 s.
 * No simula progreso: si el worker no avanza, la UI tampoco.
 */
export function useConnectorJobs(onTerminal?: (job: ConnectJob) => void): UseConnectorJobsResult {
  const [jobs, setJobs] = useState<Record<string, ConnectJob>>({});
  const timers = useRef<Record<string, ReturnType<typeof setTimeout>>>({});
  const terminalRef = useRef(onTerminal);
  terminalRef.current = onTerminal;

  const schedule = useCallback((connectorId: string, delay = 1200) => {
    if (timers.current[connectorId]) clearTimeout(timers.current[connectorId]);
    timers.current[connectorId] = setTimeout(async () => {
      try {
        const { job } = await fetchConnectStatus(connectorId);
        setJobs((prev) => ({ ...prev, [connectorId]: job }));
        if (TERMINAL.has(job.status)) {
          delete timers.current[connectorId];
          terminalRef.current?.(job);
          return;
        }
      } catch {
        // si el backend no responde, reintenta sin inventar estado
      }
      schedule(connectorId, 2000);
    }, delay);
  }, []);

  const startPolling = useCallback((connectorId: string) => {
    schedule(connectorId, 600);
  }, [schedule]);

  const clearJob = useCallback((connectorId: string) => {
    if (timers.current[connectorId]) clearTimeout(timers.current[connectorId]);
    delete timers.current[connectorId];
    setJobs((prev) => {
      const next = { ...prev };
      delete next[connectorId];
      return next;
    });
  }, []);

  useEffect(() => () => {
    Object.values(timers.current).forEach(clearTimeout);
    timers.current = {};
  }, []);

  return { jobs, startPolling, clearJob };
}
