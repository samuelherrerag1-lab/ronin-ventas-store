import type { NicheCategory, ProductFormat, ProductSKU } from '../../types/domain';

export const FORMAT_META: Record<ProductFormat, { label: string; short: string }> = {
  ebook_blueprint: { label: 'Ebook Blueprint', short: 'Blueprint' },
  boveda_arsenal: { label: 'Bóveda / Arsenal', short: 'Bóveda' },
  micro_app_html: { label: 'Micro-App HTML', short: 'App' },
  kit_sistema: { label: 'Kit / Sistema', short: 'Kit' },
  mega_bundle: { label: 'Mega Bundle', short: 'Bundle' },
  lead_magnet: { label: 'Lead Magnet', short: 'Lead' },
};

export const NICHE_META: Record<NicheCategory, { label: string; short: string }> = {
  dinero_digital_faceless: { label: 'Dinero digital faceless', short: 'Faceless' },
  ia_automatizacion_injusta: { label: 'IA & automatización injusta', short: 'IA' },
  psicologia_oscura_persuasion: { label: 'Psicología oscura & persuasión', short: 'Psicología' },
  escape_9a5_finanzas_cinicas: { label: 'Escape 9 a 5 & finanzas cínicas', short: 'Escape' },
};

export const PRICE_BANDS = [
  { value: 'all', label: 'Todos' },
  { value: 'lt20', label: '< $20' },
  { value: '20-29', label: '$20–29' },
  { value: '30plus', label: '$30+' },
];

export const FLAGSHIP = new Set(['A01', 'A02', 'A05', 'A08', 'A11', 'A12', 'E01', 'E02', 'E05', 'E08', 'B01', 'B05']);

export const inBand = (sku: ProductSKU, band: string): boolean => {
  if (band === 'lt20') return sku.price_usd < 20;
  if (band === '20-29') return sku.price_usd >= 20 && sku.price_usd < 30;
  if (band === '30plus') return sku.price_usd >= 30;
  return true;
};

export interface CatalogStats {
  total: number;
  paid: number;
  lead: number;
  routes: number;
  avg: number;
  flagship: number;
  checkout: number;
}

export const catalogStats = (products: ProductSKU[]): CatalogStats => {
  const paid = products.filter((p) => p.price_usd > 0);
  const avg = paid.length ? paid.reduce((sum, p) => sum + p.price_usd, 0) / paid.length : 0;
  return {
    total: products.length,
    paid: paid.length,
    lead: products.length - paid.length,
    routes: new Set(products.map((p) => p.bridge_route)).size,
    avg,
    flagship: products.filter((p) => FLAGSHIP.has(p.sku_id)).length,
    checkout: products.filter((p) => p.checkout_ready).length,
  };
};

export const formatCount = (products: ProductSKU[], format: string): number =>
  format === 'all' ? products.length : products.filter((p) => p.format === format).length;

export const FORMAT_ORDER: ProductFormat[] = Object.keys(FORMAT_META) as ProductFormat[];
