import type { IconName } from '../ui/Icon';

export type NavTabId =
  | 'home'
  | 'threads_clone'
  | 'pinterest_clone'
  | 'bait_studio'
  | 'catalog_factory'
  | 'publish_center'
  | 'stan_and_stealth'
  | 'metrics_radar'
  | 'brand_identity'
  | 'customizations_hub';

export type NavGroup = 'Operar' | 'Dinero' | 'Sistema';

export interface NavItem {
  id: NavTabId;
  label: string;
  short: string;
  group: NavGroup;
  icon: IconName;
  /** Verdadero si el destino necesita una acción (cola, hueco de datos, mezcla de estados). */
  action?: boolean;
}

export const NAV_ITEMS: NavItem[] = [
  { id: 'home', label: 'Command Center', short: 'Inicio', group: 'Operar', icon: 'home' },
  { id: 'threads_clone', label: 'Threads', short: 'Threads', group: 'Operar', icon: 'chat' },
  { id: 'pinterest_clone', label: 'Pinterest', short: 'Pinterest', group: 'Operar', icon: 'pin' },
  { id: 'bait_studio', label: 'Lab Anzuelos', short: 'Anzuelos', group: 'Operar', icon: 'phone' },
  { id: 'catalog_factory', label: 'Catálogo', short: 'Catálogo', group: 'Operar', icon: 'box' },
  { id: 'publish_center', label: 'Publicar', short: 'Publicar', group: 'Dinero', icon: 'upload' },
  { id: 'stan_and_stealth', label: 'Stan & Stealth', short: 'Stan', group: 'Dinero', icon: 'shield' },
  { id: 'metrics_radar', label: 'Métricas', short: 'Métricas', group: 'Dinero', icon: 'chart' },
  { id: 'brand_identity', label: 'Marca', short: 'Marca', group: 'Sistema', icon: 'brush' },
  { id: 'customizations_hub', label: 'Conectores', short: 'Conectores', group: 'Sistema', icon: 'plug' },
];

export const NAV_BY_ID = Object.fromEntries(NAV_ITEMS.map((item) => [item.id, item])) as Record<
  NavTabId,
  NavItem
>;

export const GROUPS: NavGroup[] = ['Operar', 'Dinero', 'Sistema'];

/** Destinos del dock móvil; el resto vive en la hoja "Más". */
export const MOBILE_PRIMARY: NavTabId[] = [
  'home',
  'threads_clone',
  'catalog_factory',
  'metrics_radar',
];

export const isNavTab = (value: string): value is NavTabId =>
  NAV_ITEMS.some((item) => item.id === value);
