export type ProductFormat = 'ebook_blueprint' | 'boveda_arsenal' | 'micro_app_html' | 'kit_sistema' | 'mega_bundle' | 'lead_magnet';
export type NicheCategory = 'dinero_digital_faceless' | 'ia_automatizacion_injusta' | 'psicologia_oscura_persuasion' | 'escape_9a5_finanzas_cinicas';

export interface ProductSKU {
  sku_id: string;
  slug: string;
  title: string;
  subtitle: string;
  format: ProductFormat;
  niche: NicheCategory;
  price_usd: number;
  price_cop: number;
  bridge_route: string;
  hook_angle: string;
  deliverable_spec: string;
  gumroad_url: string;
  hotmart_url: string;
  status: 'ready_spec' | 'generated' | 'published';
  featured_on_stan: boolean;
  /** Verdadero si el SKU tiene al menos una URL de checkout válida. */
  checkout_ready?: boolean;
}

export interface BaitWidgetConfig {
  widget_type: 'ios_lockscreen' | 'stripe_gumroad_dashboard' | 'iphone_note_3am' | 'micro_app_mockup';
  headline_metric: string;
  sub_metric: string;
  notifications: string[];
  timestamp_label: string;
  date_label?: string;
}

export interface ThreadsPostItem {
  post_id: string;
  strategy_lane: 'via_a_captura_anzuelo' | 'via_b_ragebait_cinico' | 'via_c_demo_microapp';
  format: 'single_text' | 'thread_chain' | 'image_bait' | 'carousel_dark';
  hook_pattern: string;
  body_slides: string[];
  suggested_self_replies: string[];
  target_sku_id: string;
  topic_tag: string;
  status: 'queued' | 'published';
  bait_widget?: BaitWidgetConfig;
  simulated_likes: number;
  simulated_replies: number;
  simulated_reposts: number;
}

export interface PinterestPinItem {
  pin_id: string;
  strategy_lane: 'dinero_ia_directo' | 'caballo_de_troya_curiosidad' | 'demo_herramienta_html';
  overlay_headline: string;
  overlay_badge: string;
  seo_title: string;
  seo_description: string;
  board_name: string;
  bridge_route: string;
  target_sku_id: string;
  visual_engine: 'playwright_html' | 'vertex_nano_banana_hybrid';
  visual_theme: string;
  aspect_ratio: '2:3' | '9:16';
  status: 'queued' | 'published';
  simulated_saves: number;
  simulated_outbound_clicks: number;
  is_competitor_benchmark: boolean;
  competitor_source: string;
  image_url?: string;
}

export interface ConnectorCard {
  connector_id: string;
  name: string;
  category: string;
  status: 'CONECTADO' | 'FALLA' | 'SIN_VERIFICAR' | string;
  auth_mode: string;
  account_label: string;
  login_url: string;
  description: string;
  capabilities: string[];
  latency_ms?: number;
  detail?: string;
  checked_at?: string;
}

export interface SkillCustomizationItem {
  skill_id: string;
  name: string;
  category: 'viral_hooks' | 'funnel_conversion' | 'stealth_antibot' | 'reverse_engineering' | 'ron_mode';
  enabled: boolean;
  installed_on_disk: boolean;
  power_rule: string;
}

export interface CompetitorTeardown {
  handle: string;
  platform: string;
  followers: number;
  cadence: string;
  real_mechanism: string;
  what_we_steal: string;
}

export interface FinopsSummary {
  project_id: string;
  total_spent_usd: number;
  circuit_breaker_limit_usd: number;
  remaining_trial_balance_usd: number | null;
  ledger_found: boolean;
  ledger_source: 'local' | 'sibling' | 'defaults' | string;
  ledger_path: string | null;
}

export interface StealthDiagnostic {
  chrome_binary_found: boolean;
  chrome_binary_path: string | null;
  persistent_vault_dir: string;
  profile_exists: boolean;
  cookies_readable: boolean;
  cookies_reason: string | null;
  domains_with_cookies: string[];
  session_cookie_count: number;
  playwright_installed: boolean;
  fingerprint_measured: boolean;
  liarjs_target_score: number | null;
}

export interface ConnectResult {
  connector_id: string;
  status: 'browser_opened' | 'chrome_not_found' | 'launch_failed' | 'not_requested' | string;
  browser_launched: boolean;
  verification: 'pending' | string;
  detail: string;
  instruction: string;
  login_url: string;
  chrome_vault_path: string;
}

export interface CustomizationsOverview {
  connectors: ConnectorCard[];
  skills: SkillCustomizationItem[];
  finops: FinopsSummary;
  stealth_Diagnostic?: StealthDiagnostic;
  competitor_teardowns: CompetitorTeardown[];
}

export interface CatalogResponse {
  total_skus: number;
  paid_skus: number;
  lead_magnets: number;
  unique_bridge_routes: number;
  /** Número de SKUs con checkout configurado (endpoint nuevo del backend). */
  checkout_ready_count?: number;
  items: ProductSKU[];
}

export interface FeedsResponse {
  threads: ThreadsPostItem[];
  pinterest: PinterestPinItem[];
}

export interface CreateBaitPostPayload {
  headline_metric: string;
  sub_metric: string;
  notifications: string[];
  widget_type?: string;
  post_text: string;
  target_sku_id?: string;
}

export interface PerformancePiece {
  piece_id: string;
  platform: string;
  sku_id?: string;
  route?: string;
  impressions: number;
  clicks: number;
  saves: number;
  ctr_percent: number;
  verdict: 'DOBLAR' | 'MATAR' | 'MUTAR' | 'OBSERVACION';
  reason: string;
}

export * from './publish';
export * from './connectors';

export interface IosRenderPayload {
  headline_metric: string;
  sub_metric: string;
  notifications: string[];
  timestamp_label?: string;
  date_label?: string;
  wallpaper_filename?: string;
  widget_type?: string;
}

export interface MetricsSummaryResponse {
  has_real_data: boolean;
  is_demo_mode: boolean;
  total_sales: number;
  total_revenue_usd: number;
  gumroad_revenue_usd: number;
  hotmart_revenue_usd: number;
  hotmart_revenue_cop: number;
  aov_usd: number | null;
  total_impressions: number;
  total_clicks: number;
  total_saves: number;
  ctr_percent: number | null;
  rpm_usd: number | null;
  doblar_o_matar_status: string;
  winning_pieces: PerformancePiece[];
  losing_pieces: PerformancePiece[];
  funnel_breakdown: Record<string, number>;
  raw_sales_count: number;
  raw_metrics_count: number;
}
