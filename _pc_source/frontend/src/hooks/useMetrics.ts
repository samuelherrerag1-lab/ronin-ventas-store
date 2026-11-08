import { useCallback, useEffect, useState } from 'react';
import { errorMessage, fetchMetricsRaw, fetchMetricsSummary } from '../api/client';
import type { MetricsRealState, MetricsSummaryResponse } from '../types/domain';

export interface MetricsState {
  summary: MetricsSummaryResponse | null;
  raw: MetricsRealState | null;
  loading: boolean;
  error: string | null;
  demo: boolean;
  setDemo: (demo: boolean) => void;
  reload: () => Promise<void>;
}

/**
 * Fuente única de las cifras de ventas: el header, el Command Center y el Radar
 * leen el mismo objeto, así una cifra mostrada dos veces nunca puede discrepar.
 */
export function useMetrics(): MetricsState {
  const [summary, setSummary] = useState<MetricsSummaryResponse | null>(null);
  const [raw, setRaw] = useState<MetricsRealState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [demo, setDemo] = useState<boolean>(() => {
    if (typeof window === 'undefined') return false;
    return new URLSearchParams(window.location.search).get('demo') === '1';
  });

  const load = useCallback(async (demoMode: boolean) => {
    setLoading(true);
    setError(null);
    const [summaryRes, rawRes] = await Promise.allSettled([
      fetchMetricsSummary(demoMode),
      fetchMetricsRaw(),
    ]);
    if (summaryRes.status === 'fulfilled') setSummary(summaryRes.value);
    else setError(errorMessage(summaryRes.reason));
    if (rawRes.status === 'fulfilled') setRaw(rawRes.value);
    else setRaw(null);
    setLoading(false);
  }, []);

  useEffect(() => {
    void load(demo);
  }, [demo, load]);

  return {
    summary,
    raw,
    loading,
    error,
    demo,
    setDemo,
    reload: () => load(demo),
  };
}
