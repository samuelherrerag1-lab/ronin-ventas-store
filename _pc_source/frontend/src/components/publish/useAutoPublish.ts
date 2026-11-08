import { useCallback, useEffect, useRef, useState } from 'react';
import { errorMessage, isPendingError } from '../../api/client';
import {
  fetchSocialJob,
  fetchSocialQueue,
  fetchSocialSchedule,
  fetchSocialSession,
  fetchSocialStatus,
  openSocialLogin,
  saveSocialSchedule,
  startSocialPublish,
  type SocialJob,
  type SocialQueueItem,
  type SocialSchedule,
  type SocialStatus,
} from './autoPublishApi';
import type { SocialPlatform as Platform } from './autoPublishApi';

const TERMINAL = new Set(['completed', 'partial', 'failed']);

export interface AutoPublishState {
  status: SocialStatus | null;
  statusError: string | null;
  statusPending: boolean;
  queue: SocialQueueItem[];
  queueError: string | null;
  queuePending: boolean;
  selected: string[];
  job: SocialJob | null;
  busy: string | null;
  notice: string | null;
  schedule: SocialSchedule | null;
  scheduleError: string | null;
  scheduleSaving: boolean;
  toggle: (id: string) => void;
  selectAll: () => void;
  clear: () => void;
  loadAll: () => void;
  openLogin: (platform: Platform) => Promise<void>;
  verify: (platform: Platform) => Promise<void>;
  publish: (dryRun: boolean) => Promise<void>;
  refreshConfig: () => Promise<void>;
  updateSchedule: (payload: Partial<SocialSchedule>) => Promise<void>;
}

export function useAutoPublish(activePlatform: Platform): AutoPublishState {
  const [status, setStatus] = useState<SocialStatus | null>(null);
  const [statusError, setStatusError] = useState<string | null>(null);
  const [statusPending, setStatusPending] = useState(false);
  const [queue, setQueue] = useState<SocialQueueItem[]>([]);
  const [queueError, setQueueError] = useState<string | null>(null);
  const [queuePending, setQueuePending] = useState(false);
  const [selected, setSelected] = useState<string[]>([]);
  const [job, setJob] = useState<SocialJob | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [schedule, setSchedule] = useState<SocialSchedule | null>(null);
  const [scheduleError, setScheduleError] = useState<string | null>(null);
  const [scheduleSaving, setScheduleSaving] = useState(false);
  const platformRef = useRef(activePlatform);
  platformRef.current = activePlatform;

  const loadStatus = useCallback(async () => {
    try {
      const data = await fetchSocialStatus();
      setStatus(data);
      setStatusError(null);
      setStatusPending(false);
    } catch (error) {
      setStatusError(errorMessage(error));
      setStatusPending(isPendingError(error));
    }
  }, []);

  const loadQueue = useCallback(async (platform: Platform) => {
    try {
      const items = await fetchSocialQueue(platform, 50);
      setQueue(items);
      setQueueError(null);
      setQueuePending(false);
      setSelected((prev) => prev.filter((id) => items.some((item) => item.id === id)));
    } catch (error) {
      setQueue([]);
      setQueueError(errorMessage(error));
      setQueuePending(isPendingError(error));
    }
  }, []);

  const refreshConfig = useCallback(async () => {
    try {
      const data = await fetchSocialSchedule();
      setSchedule(data);
      setScheduleError(null);
    } catch (error) {
      setScheduleError(errorMessage(error));
    }
  }, []);

  const loadAll = useCallback(() => {
    void loadStatus();
    void loadQueue(platformRef.current);
    void refreshConfig();
  }, [loadStatus, loadQueue, refreshConfig]);

  const loadJob = useCallback(async (jobId: string) => {
    try {
      const data = await fetchSocialJob(jobId);
      setJob(data);
      if (TERMINAL.has(data.status)) {
        void loadStatus();
        void loadQueue(platformRef.current);
      }
    } catch (error) {
      setNotice(`No se pudo leer el job: ${errorMessage(error)}`);
    }
  }, [loadQueue, loadStatus]);

  const openLogin = useCallback(async (platform: Platform) => {
    setBusy(`login-${platform}`);
    setNotice(null);
    try {
      const res = await openSocialLogin(platform);
      setNotice(res.note ?? res.detail ?? 'Ventana de login abierta.');
      void loadStatus();
    } catch (error) {
      setNotice(errorMessage(error));
    } finally {
      setBusy(null);
    }
  }, [loadStatus]);

  const verify = useCallback(async (platform: Platform) => {
    setBusy(`verify-${platform}`);
    setNotice(null);
    try {
      const fresh = await fetchSocialSession(platform, true);
      setNotice(
        fresh.logged_in
          ? `Sesión de ${platform} verificada: ${fresh.account_label ?? 'cuenta'} · ${fresh.evidence}`
          : `Sin sesión de ${platform}. Evidencia: ${fresh.evidence}`
      );
      void loadStatus();
    } catch (error) {
      setNotice(`No se pudo verificar: ${errorMessage(error)}`);
    } finally {
      setBusy(null);
    }
  }, [loadStatus]);

  const publish = useCallback(async (dryRun: boolean) => {
    const ids = selected.length > 0 ? selected : queue.slice(0, 3).map((item) => item.id);
    if (ids.length === 0) {
      setNotice('No hay piezas seleccionadas para publicar.');
      return;
    }
    setBusy('publish');
    setNotice(null);
    setJob(null);
    try {
      const res = await startSocialPublish({
        platform: platformRef.current,
        ids,
        limit: ids.length,
        dry_run: dryRun,
      });
      setNotice(res.note);
      await loadJob(res.job_id);
      void loadStatus();
    } catch (error) {
      setNotice(errorMessage(error));
    } finally {
      setBusy(null);
    }
  }, [loadJob, loadStatus, queue, selected]);

  const updateSchedule = useCallback(async (payload: Partial<SocialSchedule>) => {
    setScheduleSaving(true);
    setScheduleError(null);
    try {
      const saved = await saveSocialSchedule(payload);
      setSchedule(saved);
    } catch (error) {
      setScheduleError(errorMessage(error));
    } finally {
      setScheduleSaving(false);
    }
  }, []);

  const toggle = useCallback((id: string) => {
    setSelected((prev) => (prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]));
  }, []);
  const selectAll = useCallback(() => setSelected(queue.slice(0, 10).map((item) => item.id)), [queue]);
  const clear = useCallback(() => setSelected([]), []);

  useEffect(() => {
    void loadQueue(activePlatform);
    setSelected([]);
  }, [activePlatform, loadQueue]);

  useEffect(() => {
    void loadStatus();
    void refreshConfig();
    const timer = window.setInterval(() => void loadStatus(), 15000);
    return () => window.clearInterval(timer);
  }, [loadStatus, refreshConfig]);

  useEffect(() => {
    if (!job || TERMINAL.has(job.status)) return undefined;
    const timer = window.setInterval(() => void loadJob(job.job_id), 2500);
    return () => window.clearInterval(timer);
  }, [job, loadJob]);

  return {
    status,
    statusError,
    statusPending,
    queue,
    queueError,
    queuePending,
    selected,
    job,
    busy,
    notice,
    schedule,
    scheduleError,
    scheduleSaving,
    toggle,
    selectAll,
    clear,
    loadAll,
    openLogin,
    verify,
    publish,
    refreshConfig,
    updateSchedule,
  };
}
