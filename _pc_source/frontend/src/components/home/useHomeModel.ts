import { useMemo } from 'react';
import type {
  CustomizationsOverview,
  MetricsRealState,
  MetricsSummaryResponse,
  PinterestPinItem,
  ProductSKU,
  ThreadsPostItem,
} from '../../types/domain';
import type { IconName } from '../ui/Icon';
import { buildPieces, buildSeries, sumSeries, type DayPoint, type PieceRow, type Totals } from '../metrics/metricsModel';
import { buildRoutes, halfDelta, pctOf, type RouteRow } from './homeModelUtils';
import { clamp } from '../../utils/format';

export type { RouteRow } from './homeModelUtils';

export interface KpiDef {
  key: 'revenue' | 'sales' | 'impressions' | 'ctr';
  label: string;
  hint: string;
  format: 'usd' | 'int' | 'pct';
  value: number | null;
  spark: number[];
  delta: number | null;
  goodDirection: 'up' | 'down';
  tone: 'accent' | 'ink';
}

export interface HomeAction {
  id: string;
  title: string;
  hint: string;
  icon: IconName;
  tone: 'accent' | 'warn' | 'mute';
  tab: string;
}

export interface HomeModel {
  hasData: boolean;
  demo: boolean;
  series: DayPoint[];
  totals: Totals;
  kpis: KpiDef[];
  funnel: { key: string; label: string; value: number; rate: number | null; tone: 'mute' | 'accent' }[];
  counts: { doblar: number; matar: number; mutar: number };
  ctr: number | null;
  trigger: PieceRow | null;
  triggerKind: 'double' | 'kill' | null;
  finding: string;
  actions: HomeAction[];
  routes: RouteRow[];
}

export function useHomeModel(args: {
  products: ProductSKU[];
  threads: ThreadsPostItem[];
  pins: PinterestPinItem[];
  customizations: CustomizationsOverview | null;
  summary: MetricsSummaryResponse | null;
  raw: MetricsRealState | null;
  demo: boolean;
}): HomeModel {
  const { products, threads, pins, customizations, summary, raw, demo } = args;

  return useMemo(() => {
    const series = buildSeries(raw, demo, summary, 14);
    const totals = sumSeries(series);
    const pieces = buildPieces(summary, raw);
    const hasData = Boolean(summary?.has_real_data) && !demo;

    const imp = series.map((p) => p.impressions);
    const clk = series.map((p) => p.clicks);
    const rev = series.map((p) => p.revenue);
    const sales = series.map((p) => p.sales);
    const ctrSeries = series.map((p) => (p.impressions > 0 ? (p.clicks / p.impressions) * 100 : 0));

    const ctr = totals.ctr;
    const kpis: KpiDef[] = [
      {
        key: 'revenue',
        label: 'Ingresos',
        hint: 'Gumroad + Hotmart del periodo',
        format: 'usd',
        value: summary ? summary.total_revenue_usd : null,
        spark: rev,
        delta: halfDelta(rev),
        goodDirection: 'up',
        tone: 'accent',
      },
      {
        key: 'sales',
        label: 'Ventas',
        hint: 'Órdenes pagadas (incluye order bumps)',
        format: 'int',
        value: summary ? summary.total_sales : null,
        spark: sales,
        delta: halfDelta(sales),
        goodDirection: 'up',
        tone: 'ink',
      },
      {
        key: 'impressions',
        label: 'Impresiones',
        hint: 'Threads + Pinterest',
        format: 'int',
        value: summary ? summary.total_impressions : null,
        spark: imp,
        delta: halfDelta(imp),
        goodDirection: 'up',
        tone: 'ink',
      },
      {
        key: 'ctr',
        label: 'CTR saliente',
        hint: 'Clics ÷ impresiones',
        format: 'pct',
        value: ctr,
        spark: ctrSeries,
        delta: halfDelta(ctrSeries),
        goodDirection: 'up',
        tone: 'ink',
      },
    ];

    const clicks = summary?.total_clicks ?? 0;
    const salesCount = summary?.total_sales ?? 0;
    const impressions = summary?.total_impressions ?? 0;
    const funnel = [
      { key: 'impressions', label: 'Impresiones', value: impressions, rate: null, tone: 'mute' as const },
      { key: 'clicks', label: 'Clics', value: clicks, rate: pctOf(clicks, impressions), tone: 'mute' as const },
      { key: 'sales', label: 'Ventas', value: salesCount, rate: pctOf(salesCount, clicks), tone: 'accent' as const },
    ];

    const counts = {
      doblar: pieces.filter((p) => p.verdict === 'DOBLAR').length,
      matar: pieces.filter((p) => p.verdict === 'MATAR').length,
      mutar: pieces.filter((p) => p.verdict === 'MUTAR').length,
    };
    // El backend puede traer piezas ganadoras sin duplicarlas en la tabla: se suman una sola vez.
    if (pieces.length === 0 && summary) {
      counts.doblar = summary.winning_pieces.length;
      counts.matar = summary.losing_pieces.filter((p) => p.verdict === 'MATAR').length;
      counts.mutar = summary.losing_pieces.filter((p) => p.verdict === 'MUTAR').length;
    }

    const worst = [...pieces].filter((p) => p.impressions > 0).sort((a, b) => a.ctr - b.ctr)[0] ?? null;
    const best = [...pieces].filter((p) => p.impressions > 0).sort((a, b) => b.ctr - a.ctr)[0] ?? null;
    const triggerKind: HomeModel['triggerKind'] = worst && worst.ctr < 0.8 ? 'kill' : best ? 'double' : null;
    const trigger = triggerKind === 'kill' ? worst : triggerKind === 'double' ? best : null;

    const checkoutMissing = products.filter((p) => p.price_usd > 0 && !p.checkout_ready).length;
    const connectors = customizations?.connectors ?? [];
    const connectorsPending = connectors.filter((c) => !c.checked_at).length;
    const queued = threads.filter((t) => t.status === 'queued').length + pins.filter((p) => p.status === 'queued').length;

    const actions: HomeAction[] = [];
    if (!hasData) {
      actions.push({
        id: 'import',
        title: 'Importar ventas reales',
        hint: 'CSV de Gumroad o Hotmart · sin cifras inventadas',
        icon: 'download',
        tone: 'accent',
        tab: 'metrics_radar',
      });
    }
    if (checkoutMissing > 0) {
      actions.push({
        id: 'checkout',
        title: `${checkoutMissing} SKU sin checkout configurado`,
        hint: 'Rutas listas, falta URL de Gumroad o Hotmart',
        icon: 'cart',
        tone: 'warn',
        tab: 'publish_center',
      });
    }
    if (connectorsPending > 0) {
      actions.push({
        id: 'connect',
        title: `${connectorsPending} conectores sin verificar`,
        hint: 'SSO en Chrome persistente',
        icon: 'plug',
        tone: 'mute',
        tab: 'customizations_hub',
      });
    }
    if (queued > 0) {
      actions.push({
        id: 'queue',
        title: `${queued} piezas en cola`,
        hint: 'Copiar y publicar desde el feed',
        icon: 'bell',
        tone: 'mute',
        tab: 'threads_clone',
      });
    }
    actions.push({
      id: 'bait',
      title: 'Generar captura anzuelo',
      hint: 'iOS 17.5 · Vertex Nano Banana 2',
      icon: 'phone',
      tone: 'mute',
      tab: 'bait_studio',
    });

    const routes = buildRoutes(pieces);

    const finding = !hasData && !demo
      ? 'Sin datos reales todavía. Importa un CSV de Gumroad o Hotmart para activar el criterio de 14 días.'
      : counts.matar > 0
        ? `${counts.doblar} pieza${counts.doblar === 1 ? '' : 's'} para doblar y ${counts.matar} en umbral de muerte. La ventana de decisión es de 14 días.`
        : `${counts.doblar} pieza${counts.doblar === 1 ? '' : 's'} por encima del 2,0% de CTR. Nada en umbral de muerte.`;

    return {
      hasData,
      demo,
      series,
      totals,
      kpis,
      funnel,
      counts,
      ctr: clamp(ctr ?? 0, 0, 100),
      trigger,
      triggerKind,
      finding,
      actions: actions.slice(0, 4),
      routes,
    };
  }, [products, threads, pins, customizations, summary, raw, demo]);
}
