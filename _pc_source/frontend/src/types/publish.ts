/**
 * Contrato de tipos del Publish Center (publicación honesta).
 * El backend expone estos endpoints; si aún no existe alguno, el cliente
 * de API lo reporta como "pendiente" en lugar de romper la vista.
 */

export type PublishPlatform = 'threads' | 'pinterest';
export type PublishItemStatus = 'queued' | 'published' | (string & {});

export interface PublishCheck {
  id: string;
  label: string;
  ok: boolean;
  detail?: string;
}

export interface PublishCounts {
  skus?: number;
  paid?: number;
  leads?: number;
  checkouts?: number;
  threads?: number;
  pins?: number;
  art_covers?: number;
  deliverables?: number;
  [key: string]: number | undefined;
}

export interface PublishReadiness {
  ready: boolean;
  checks: PublishCheck[];
  blockers: string[];
  counts: PublishCounts;
  next_actions: string[];
}

export interface PublishKitItem {
  id: string;
  platform: PublishPlatform | string;
  text: string;
  image_url: string | null;
  target_route: string;
  target_sku_id: string;
  status: PublishItemStatus;
}

export interface PublishKitResponse {
  items: PublishKitItem[];
  note?: string;
  platform?: string;
  count?: number;
  base_url?: string;
  published_to_network?: boolean;
  tracking?: string;
}

export interface PublishMarkPayload {
  platform: string;
  item_id: string;
  status: 'published' | 'queued';
}

export interface PublishMarkResponse {
  platform?: string;
  item_id?: string;
  status?: string;
  note?: string;
  persisted?: boolean;
  tracked_locally?: boolean;
  published_to_network?: boolean;
  publication_url?: string | null;
}

export interface CheckoutPayload {
  gumroad_url?: string;
  hotmart_url?: string;
}

export interface CheckoutSaveResponse {
  sku_id?: string;
  gumroad_url?: string;
  hotmart_url?: string;
  checkout_ready?: boolean;
}

export interface CheckoutBulkLink {
  gumroad_url?: string;
  hotmart_url?: string;
}

export interface CheckoutBulkError {
  sku_id?: string;
  reason?: string;
}

export interface CheckoutBulkResponse {
  updated?: number;
  skipped?: number;
  errors?: CheckoutBulkError[];
  checkout_ready_count?: number;
  paid_skus?: number;
  note?: string;
  detail?: string;
}

export interface SiteManifest {
  generated_at?: string;
  base_url?: string;
  skus?: number;
  paid_skus?: number;
  lead_magnets?: number;
  /** El backend puede devolver el conteo o la lista de rutas. */
  routes?: number | string[];
  files?: number;
  checkout_ready?: number;
  blockers?: string[];
  manifest_path?: string;
  [key: string]: unknown;
}

export interface PublishExportResponse {
  status?: string;
  base_url?: string;
  manifest?: SiteManifest;
  manifest_path?: string;
  [key: string]: unknown;
}

export interface HealthResponse {
  status?: string;
  system?: string;
  block?: number;
  lan_ip?: string;
  lan_url?: string;
  frontend_built?: boolean;
  publish_site_ready?: boolean;
  vertex?: {
    project_id?: string;
    location?: string;
    model?: string;
    fallback_model?: string;
    adc_present?: boolean;
  };
}
