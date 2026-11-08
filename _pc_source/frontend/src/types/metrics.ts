import type { PerformancePiece } from './domain';

export interface SaleRecord {
  id: string;
  source: 'gumroad' | 'hotmart';
  order_id: string;
  date: string;
  product_name: string;
  sku_id?: string | null;
  amount_usd: number;
  amount_cop?: number | null;
  currency: string;
  is_order_bump: boolean;
  customer_email?: string | null;
}

export interface PieceMetricRecord {
  id: string;
  date: string;
  platform: 'threads' | 'pinterest';
  piece_id: string;
  sku_id?: string | null;
  route?: string | null;
  impressions: number;
  clicks: number;
  saves: number;
  notes?: string | null;
}

/** `/api/metrics/raw` — filas crudas con fecha, base de la serie temporal. */
export interface MetricsRealState {
  sales: SaleRecord[];
  manual_piece_metrics: PieceMetricRecord[];
  last_updated?: string | null;
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
  attribution_note?: string;
}
