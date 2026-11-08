import { useCallback, useEffect, useState } from 'react';
import {
  errorMessage,
  isPendingError,
} from '../../api/client';
import {
  exportPublishSite,
  fetchPublishKit,
  fetchPublishReadiness,
  fetchPublishSiteManifest,
  markPublishItem,
} from '../../api/publish';
import type {
  PublishKitItem,
  PublishPlatform,
  PublishReadiness,
  SiteManifest,
} from '../../types/domain';

interface AsyncSlot<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  pending: boolean;
}

const emptySlot = <T,>(): AsyncSlot<T> => ({ data: null, loading: false, error: null, pending: false });

function slotFromError<T>(error: unknown): AsyncSlot<T> {
  return {
    data: null,
    loading: false,
    error: errorMessage(error),
    pending: isPendingError(error),
  };
}

export interface PublishCenterState {
  readiness: AsyncSlot<PublishReadiness>;
  kits: Record<PublishPlatform, AsyncSlot<PublishKitItem[]>>;
  manifest: AsyncSlot<SiteManifest>;
  exporting: boolean;
  exportError: string | null;
  exportPending: boolean;
  exportResult: SiteManifest | null;
  markNote: string | null;
  markingId: string | null;
  loadReadiness: () => Promise<void>;
  loadKit: (platform: PublishPlatform) => Promise<void>;
  loadManifest: () => Promise<void>;
  loadAll: () => Promise<void>;
  runExport: () => Promise<void>;
  markItem: (platform: PublishPlatform, item: PublishKitItem) => Promise<void>;
}

const PLATFORMS: PublishPlatform[] = ['threads', 'pinterest'];

export function usePublishCenter(): PublishCenterState {
  const [readiness, setReadiness] = useState<AsyncSlot<PublishReadiness>>(emptySlot());
  const [kits, setKits] = useState<Record<PublishPlatform, AsyncSlot<PublishKitItem[]>>>({
    threads: emptySlot(),
    pinterest: emptySlot(),
  });
  const [manifest, setManifest] = useState<AsyncSlot<SiteManifest>>(emptySlot());
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);
  const [exportPending, setExportPending] = useState(false);
  const [exportResult, setExportResult] = useState<SiteManifest | null>(null);
  const [markNote, setMarkNote] = useState<string | null>(null);
  const [markingId, setMarkingId] = useState<string | null>(null);

  const loadReadiness = useCallback(async () => {
    setReadiness((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const data = await fetchPublishReadiness();
      setReadiness({ data, loading: false, error: null, pending: false });
    } catch (error) {
      setReadiness(slotFromError(error));
    }
  }, []);

  const loadKit = useCallback(async (platform: PublishPlatform) => {
    setKits((prev) => ({ ...prev, [platform]: { ...prev[platform], loading: true, error: null } }));
    try {
      const res = await fetchPublishKit(platform, 50);
      setKits((prev) => ({
        ...prev,
        [platform]: { data: res.items ?? [], loading: false, error: null, pending: false },
      }));
    } catch (error) {
      setKits((prev) => ({ ...prev, [platform]: slotFromError(error) }));
    }
  }, []);

  const loadManifest = useCallback(async () => {
    setManifest((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const data = await fetchPublishSiteManifest();
      setManifest({ data, loading: false, error: null, pending: false });
    } catch (error) {
      setManifest(slotFromError(error));
    }
  }, []);

  const loadAll = useCallback(async () => {
    await Promise.all([loadReadiness(), loadKit('threads'), loadKit('pinterest'), loadManifest()]);
  }, [loadReadiness, loadKit, loadManifest]);

  const runExport = useCallback(async () => {
    setExporting(true);
    setExportError(null);
    setExportPending(false);
    setExportResult(null);
    try {
      const res = await exportPublishSite();
      const result = (res.manifest ?? res) as SiteManifest;
      setExportResult(result);
      await Promise.all([loadManifest(), loadReadiness()]);
    } catch (error) {
      setExportPending(isPendingError(error));
      setExportError(errorMessage(error));
    } finally {
      setExporting(false);
    }
  }, [loadManifest, loadReadiness]);

  const markItem = useCallback(async (platform: PublishPlatform, item: PublishKitItem) => {
    setMarkingId(item.id);
    setMarkNote(null);
    try {
      const res = await markPublishItem({
        platform,
        item_id: item.id,
        status: 'published',
      });
      setKits((prev) => {
        const slot = prev[platform];
        if (!slot.data) return prev;
        return {
          ...prev,
          [platform]: {
            ...slot,
            data: slot.data.map((it) =>
              it.id === item.id ? { ...it, status: res.status ?? 'published' } : it
            ),
          },
        };
      });
      setMarkNote(
        res.note ??
          'Seguimiento local guardado. No se publicó en la red social: la publicación es manual.'
      );
    } catch (error) {
      setMarkNote(`No se pudo guardar el seguimiento: ${errorMessage(error)}`);
    } finally {
      setMarkingId(null);
    }
  }, []);

  useEffect(() => {
    void loadAll();
  }, [loadAll]);

  return {
    readiness,
    kits: Object.fromEntries(
      PLATFORMS.map((p) => [p, kits[p]])
    ) as Record<PublishPlatform, AsyncSlot<PublishKitItem[]>>,
    manifest,
    exporting,
    exportError,
    exportPending,
    exportResult,
    markNote,
    markingId,
    loadReadiness,
    loadKit,
    loadManifest,
    loadAll,
    runExport,
    markItem,
  };
}
