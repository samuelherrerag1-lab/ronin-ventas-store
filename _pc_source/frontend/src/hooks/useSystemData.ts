import { useCallback, useEffect, useState } from 'react';
import {
  connectProvider,
  createThreadFromBait,
  errorMessage,
  fetchCatalog,
  fetchCustomizations,
  fetchFeeds,
  fetchHealth,
  generateVertexImage,
  mutateThreadHook,
  togglePinStatus,
  toggleSkill,
  toggleStanFeatured,
  toggleThreadStatus,
} from '../api/client';
import type {
  ConnectResult,
  CreateBaitPostPayload,
  CustomizationsOverview,
  HealthResponse,
  PinterestPinItem,
  ProductSKU,
  ThreadsPostItem,
} from '../types/domain';

export interface SystemData {
  products: ProductSKU[];
  threads: ThreadsPostItem[];
  pins: PinterestPinItem[];
  customizations: CustomizationsOverview | null;
  health: HealthResponse | null;
  lanUrl: string;
  loading: boolean;
  loadError: string | null;
  actionError: string | null;
  loadAll: () => Promise<void>;
  loadCatalog: () => Promise<void>;
  clearActionError: () => void;
  mutateHook: (id: string) => Promise<void>;
  toggleThread: (id: string) => Promise<void>;
  togglePin: (id: string) => Promise<void>;
  toggleStan: (id: string) => Promise<void>;
  connect: (id: string) => Promise<ConnectResult>;
  toggleSkillById: (id: string, enabled: boolean) => Promise<void>;
  createBait: (payload: CreateBaitPostPayload) => Promise<void>;
  generateVertex: (prompt: string, aspect: string) => Promise<Awaited<ReturnType<typeof generateVertexImage>>>;
}

/** Carga y muta los datos reales del sistema, con errores visibles y reintento. */
export function useSystemData(onBaitCreated?: () => void): SystemData {
  const [products, setProducts] = useState<ProductSKU[]>([]);
  const [threads, setThreads] = useState<ThreadsPostItem[]>([]);
  const [pins, setPins] = useState<PinterestPinItem[]>([]);
  const [customizations, setCustomizations] = useState<CustomizationsOverview | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [lanUrl, setLanUrl] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const loadCatalog = useCallback(async () => {
    try {
      const cat = await fetchCatalog();
      setProducts(cat.items);
    } catch (error) {
      setActionError(`No se pudo recargar el catálogo: ${errorMessage(error)}`);
    }
  }, []);

  const loadAll = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    const [catalogRes, feedsRes, custRes, healthRes] = await Promise.allSettled([
      fetchCatalog(),
      fetchFeeds(true),
      fetchCustomizations(),
      fetchHealth(),
    ]);
    const failures: string[] = [];
    if (catalogRes.status === 'fulfilled') setProducts(catalogRes.value.items);
    else failures.push(`catálogo: ${errorMessage(catalogRes.reason)}`);
    if (feedsRes.status === 'fulfilled') {
      setThreads(feedsRes.value.threads);
      setPins(feedsRes.value.pinterest);
    } else failures.push(`feeds: ${errorMessage(feedsRes.reason)}`);
    if (custRes.status === 'fulfilled') setCustomizations(custRes.value);
    else failures.push(`conectores: ${errorMessage(custRes.reason)}`);
    if (healthRes.status === 'fulfilled') {
      setHealth(healthRes.value);
      setLanUrl(healthRes.value.lan_url ?? '');
    } else failures.push(`health: ${errorMessage(healthRes.reason)}`);
    if (failures.length > 0) setLoadError(failures.join(' | '));
    setLoading(false);
  }, []);

  useEffect(() => {
    void loadAll();
  }, [loadAll]);

  const action = useCallback(async (label: string, run: () => Promise<void>) => {
    setActionError(null);
    try {
      await run();
    } catch (error) {
      setActionError(`${label}: ${errorMessage(error)}`);
    }
  }, []);

  const mutateHook = (id: string) =>
    action('No se pudo mutar el hook', async () => {
      const updated = await mutateThreadHook(id);
      setThreads((prev) => prev.map((t) => (t.post_id === id ? updated : t)));
    });

  const toggleThread = (id: string) =>
    action('No se pudo cambiar el seguimiento del post', async () => {
      const updated = await toggleThreadStatus(id);
      setThreads((prev) => prev.map((t) => (t.post_id === id ? updated : t)));
    });

  const togglePin = (id: string) =>
    action('No se pudo cambiar el seguimiento del pin', async () => {
      const updated = await togglePinStatus(id);
      setPins((prev) => prev.map((pin) => (pin.pin_id === id ? updated : pin)));
    });

  const toggleStan = async (id: string) => {
    await action('No se pudo actualizar el catálogo (Stan)', async () => {
      const updated = await toggleStanFeatured(id);
      setProducts((prev) => prev.map((pr) => (pr.sku_id === id ? updated : pr)));
    });
  };

  const connect = async (id: string) => {
    const result = await connectProvider(id, true);
    setCustomizations(await fetchCustomizations());
    return result;
  };

  const toggleSkillById = async (id: string, enabled: boolean) => {
    await action('No se pudo cambiar la skill', async () => {
      await toggleSkill(id, enabled);
      setCustomizations(await fetchCustomizations());
    });
  };

  const createBait = async (payload: CreateBaitPostPayload) => {
    const created = await createThreadFromBait(payload);
    setThreads((prev) => [created, ...prev]);
    onBaitCreated?.();
  };

  return {
    products,
    threads,
    pins,
    customizations,
    health,
    lanUrl,
    loading,
    loadError,
    actionError,
    loadAll,
    loadCatalog,
    clearActionError: () => setActionError(null),
    mutateHook,
    toggleThread,
    togglePin,
    toggleStan,
    connect,
    toggleSkillById,
    createBait,
    generateVertex: generateVertexImage,
  };
}
