import type {
  CatalogResponse,
  ConnectResult,
  ConnectorTestResult,
  CreateBaitPostPayload,
  CustomizationsOverview,
  FeedsResponse,
  HealthResponse,
  IosRenderPayload,
  PinterestPinItem,
  ProductSKU,
  SkillCustomizationItem,
  TestAllResponse,
  ThreadsPostItem,
} from '../types/domain';

import { ApiError, extractErrorDetail } from './errors';

export type { ConnectJob, ConnectorTestResult, TestAllResponse } from '../types/domain';
export { ApiError, errorMessage, isApiError, isPendingError } from './errors';

const BASE_URL = typeof window !== 'undefined' && window.location.port === '5175'
  ? 'http://127.0.0.1:8765'
  : '';

export async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE_URL}${path}`, {
      headers: { 'Content-Type': 'application/json', ...(options?.headers || {}) },
      ...options,
    });
  } catch {
    throw new ApiError(path, 0, 'Sin conexión con el backend en 127.0.0.1:8765. Arranca el servidor y reintenta.');
  }

  const contentType = res.headers.get('content-type') || '';
  const isJson = contentType.includes('application/json');

  if (!res.ok) {
    const body = await res.text().catch(() => '');
    const detail = extractErrorDetail(body, isJson);
    const pending = res.status === 404 || res.status === 503;
    throw new ApiError(path, res.status, detail || res.statusText, pending);
  }

  if (!isJson) {
    // El backend sirve el index.html del SPA como catch-all: el endpoint no existe.
    throw new ApiError(path, 404, 'El endpoint no existe todavía en el backend.', true);
  }

  return res.json() as Promise<T>;
}

export async function fetchHealth(): Promise<HealthResponse> {
  return request<HealthResponse>('/api/health');
}

export async function fetchCatalog(formatFilter?: string, nicheFilter?: string): Promise<CatalogResponse> {
  const params = new URLSearchParams();
  if (formatFilter && formatFilter !== 'all') params.append('format_filter', formatFilter);
  if (nicheFilter && nicheFilter !== 'all') params.append('niche_filter', nicheFilter);
  const qs = params.toString() ? `?${params.toString()}` : '';
  return request<CatalogResponse>(`/api/catalog${qs}`);
}

export async function toggleStanFeatured(skuId: string): Promise<ProductSKU> {
  return request<ProductSKU>(`/api/catalog/${encodeURIComponent(skuId)}/toggle-stan`, { method: 'POST' });
}

export async function generateSkuDeliverable(skuId: string): Promise<{
  sku_id: string;
  status: string;
  filename: string;
  deliverable_url: string;
  bytes: number;
}> {
  return request(`/api/catalog/${encodeURIComponent(skuId)}/generate-deliverable`, { method: 'POST' });
}

export async function fetchFeeds(includeBenchmarks = true): Promise<FeedsResponse> {
  return request<FeedsResponse>(`/api/feeds?include_benchmarks=${includeBenchmarks}`);
}

export async function mutateThreadHook(postId: string): Promise<ThreadsPostItem> {
  return request<ThreadsPostItem>(`/api/feeds/threads/${encodeURIComponent(postId)}/mutate-hook`, { method: 'POST' });
}

export async function toggleThreadStatus(postId: string): Promise<ThreadsPostItem> {
  return request<ThreadsPostItem>(`/api/feeds/threads/${encodeURIComponent(postId)}/toggle-status`, { method: 'POST' });
}

export async function togglePinStatus(pinId: string): Promise<PinterestPinItem> {
  return request<PinterestPinItem>(`/api/feeds/pinterest/${encodeURIComponent(pinId)}/toggle-status`, { method: 'POST' });
}

export async function createThreadFromBait(payload: CreateBaitPostPayload): Promise<ThreadsPostItem> {
  return request<ThreadsPostItem>('/api/feeds/threads/from-bait', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function fetchCustomizations(): Promise<CustomizationsOverview> {
  return request<CustomizationsOverview>('/api/customizations');
}

export async function connectProvider(
  connectorId: string,
  launchBrowser = true
): Promise<ConnectResult> {
  return request<ConnectResult>(`/api/customizations/connect/${encodeURIComponent(connectorId)}`, {
    method: 'POST',
    body: JSON.stringify({ launch_browser: launchBrowser }),
  });
}

export async function toggleSkill(skillId: string, enabled: boolean): Promise<SkillCustomizationItem> {
  return request<SkillCustomizationItem>(`/api/customizations/skills/${encodeURIComponent(skillId)}/toggle`, {
    method: 'POST',
    body: JSON.stringify({ enabled }),
  });
}

export async function generateVertexImage(
  prompt: string,
  aspectRatio = '3:4'
): Promise<{
  image_url: string;
  status: string;
  latency_sec?: number;
  elapsed_attempt_sec?: number;
  model?: string;
  estimated_cost_usd?: number;
  spent_total_usd?: number;
}> {
  return request('/api/customizations/vertex-generate', {
    method: 'POST',
    body: JSON.stringify({ prompt, aspect_ratio: aspectRatio }),
  });
}

export async function renderIosPng(payload: IosRenderPayload): Promise<{
  status: string;
  filename: string;
  image_url: string;
  resolution: string;
}> {
  return request('/api/customizations/render-ios-png', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function fetchConnectStatus(connectorId: string): Promise<{
  job: import('../types/domain').ConnectJob;
  secrets: Record<string, unknown>;
}> {
  return request(`/api/customizations/connect/${encodeURIComponent(connectorId)}/status`);
}

export async function stopConnect(connectorId: string): Promise<import('../types/domain').ConnectJob> {
  return request(`/api/customizations/connect/${encodeURIComponent(connectorId)}/stop`, { method: 'POST' });
}

export async function fetchSecrets(): Promise<Record<string, Record<string, unknown>>> {
  return request('/api/customizations/secrets');
}

export async function testConnector(connectorId: string): Promise<ConnectorTestResult> {
  return request<ConnectorTestResult>(`/api/customizations/test/${encodeURIComponent(connectorId)}`, { method: 'POST' });
}

export async function testAllConnectors(): Promise<TestAllResponse> {
  return request<TestAllResponse>('/api/customizations/test-all', { method: 'POST' });
}

export async function fetchMetricsSummary(demo = false): Promise<import('../types/domain').MetricsSummaryResponse> {
  return request<import('../types/domain').MetricsSummaryResponse>(`/api/metrics?demo=${demo}`);
}

export async function importSalesCsv(
  source: 'gumroad' | 'hotmart',
  csvContent: string
): Promise<Record<string, unknown>> {
  return request('/api/metrics/import-csv', {
    method: 'POST',
    body: JSON.stringify({ source, csv_content: csvContent }),
  });
}

export async function createManualMetric(payload: {
  date: string;
  platform: 'threads' | 'pinterest';
  piece_id: string;
  sku_id?: string;
  route?: string;
  impressions: number;
  clicks: number;
  saves: number;
  notes?: string;
}): Promise<Record<string, unknown>> {
  return request('/api/metrics/manual-entry', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function resetMetrics(): Promise<Record<string, unknown>> {
  return request('/api/metrics/reset', { method: 'DELETE' });
}

export async function fetchCsvTemplates(): Promise<Record<string, unknown>> {
  return request('/api/metrics/templates');
}
