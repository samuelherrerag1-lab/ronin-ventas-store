/** Contratos y constantes del Identity Studio. Sin estado, sin efectos. */

export type VariantId = 'avatar' | 'banner' | 'og' | 'pin' | 'favicon';

export interface VariantSpec {
  id: VariantId;
  label: string;
  detail: string;
  width: number;
  height: number;
  use: string;
  filename: string;
}

export interface AvatarBackground {
  id: string;
  label: string;
  hex: string;
  ring: string;
}

export interface BrandCopy {
  name: string;
  handle: string;
  tagline: string;
}

export interface ImageMeta {
  name: string;
  size: number;
  width: number;
  height: number;
}

/** Límite duro de entrada. Se valida antes de decodificar nada. */
export const MAX_FILE_BYTES = 10 * 1024 * 1024;

export const BRAND: BrandCopy = {
  name: 'Ron Overthinks',
  handle: '@ronoverthinks',
  tagline: 'Sistemas de ingresos digitales. Cero postureo.',
};

export const SUITE_LABEL = 'RONIN VENTAS OS';

export const VARIANTS: VariantSpec[] = [
  {
    id: 'avatar', label: 'Avatar 1:1', detail: '512 × 512', width: 512, height: 512,
    use: 'Threads · Gumroad · Hotmart', filename: 'avatar-512.png',
  },
  {
    id: 'banner', label: 'Banner Threads', detail: '1500 × 500', width: 1500, height: 500,
    use: 'Cabecera con espacio para el avatar', filename: 'threads-banner-1500x500.png',
  },
  {
    id: 'og', label: 'Open Graph', detail: '1200 × 630', width: 1200, height: 630,
    use: 'Tarjetas de enlace y previews', filename: 'open-graph-1200x630.png',
  },
  {
    id: 'pin', label: 'Pin Pinterest', detail: '1000 × 1500', width: 1000, height: 1500,
    use: 'Pin vertical 2:3', filename: 'pinterest-pin-1000x1500.png',
  },
  {
    id: 'favicon', label: 'Favicon', detail: '64 × 64', width: 64, height: 64,
    use: 'Pestaña del navegador', filename: 'favicon-64.png',
  },
];

export const AVATAR_BACKGROUNDS: AvatarBackground[] = [
  { id: 'negro', label: 'Negro', hex: '#08080C', ring: 'rgba(255,255,255,0.22)' },
  { id: 'terracota', label: 'Terracota', hex: '#E07A5F', ring: 'rgba(0,0,0,0.22)' },
  { id: 'esmeralda', label: 'Esmeralda', hex: '#10B981', ring: 'rgba(0,0,0,0.22)' },
  { id: 'blanco', label: 'Blanco', hex: '#F5F3EF', ring: 'rgba(0,0,0,0.14)' },
];

/** Nombre de archivo estable a partir del nombre de marca. */
export function slugify(value: string): string {
  const slug = value
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
  return slug || 'ronin-brand';
}

export function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}
