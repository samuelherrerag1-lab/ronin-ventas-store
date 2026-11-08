import { request } from './client';
import type {
  CheckoutBulkLink,
  CheckoutBulkResponse,
  CheckoutPayload,
  CheckoutSaveResponse,
  PublishExportResponse,
  PublishKitResponse,
  PublishMarkPayload,
  PublishMarkResponse,
  PublishPlatform,
  PublishReadiness,
  SiteManifest,
} from '../types/domain';

/**
 * Contrato del Publish Center (backend-core). Si el endpoint aún no existe, el
 * client lanza ApiError con `pending=true` y la vista muestra "Pendiente en backend".
 */

export async function fetchPublishReadiness(): Promise<PublishReadiness> {
  return request<PublishReadiness>('/api/publish/readiness');
}

export async function fetchPublishKit(
  platform: PublishPlatform,
  limit = 50
): Promise<PublishKitResponse> {
  return request<PublishKitResponse>(
    `/api/publish/kit?platform=${encodeURIComponent(platform)}&limit=${limit}`
  );
}

export async function markPublishItem(payload: PublishMarkPayload): Promise<PublishMarkResponse> {
  return request<PublishMarkResponse>('/api/publish/mark', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function exportPublishSite(): Promise<PublishExportResponse> {
  return request<PublishExportResponse>('/api/publish/export-site', { method: 'POST' });
}

export async function fetchPublishSiteManifest(): Promise<SiteManifest> {
  return request<SiteManifest>('/api/publish/site-manifest');
}

export async function saveSkuCheckout(
  skuId: string,
  payload: CheckoutPayload
): Promise<CheckoutSaveResponse> {
  return request<CheckoutSaveResponse>(`/api/catalog/${encodeURIComponent(skuId)}/checkout`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function saveCheckoutBulk(
  links: Record<string, CheckoutBulkLink>
): Promise<CheckoutBulkResponse> {
  return request<CheckoutBulkResponse>('/api/catalog/checkout-bulk', {
    method: 'POST',
    body: JSON.stringify({ links }),
  });
}
