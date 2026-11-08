import type { ConnectorCard } from '../../types/domain';

const SHORT_NAMES: Record<string, string> = {
  google_master: 'Google SSO',
  threads: 'Threads',
  pinterest: 'Pinterest',
  gumroad: 'Gumroad',
  hotmart: 'Hotmart',
  vertex_ai: 'Vertex AI',
  opencode_v2: 'OpenCode V2',
  github_pages: 'GitHub Pages',
};

const SUBTITLES: Record<string, string> = {
  google_master: 'Vault persistente',
  threads: '@ronoverthinks',
  pinterest: 'Pinterest Business',
  gumroad: 'Checkout global · USD',
  hotmart: 'Checkout LatAm · COP',
  vertex_ai: 'Nano Banana 2',
  opencode_v2: 'Fábrica local',
  github_pages: 'Deploy estático',
};

const CATEGORY_LABELS: Record<string, string> = {
  auth_sso: 'Acceso',
  social_network: 'Social',
  checkout_gateway: 'Cobros',
  ai_cloud: 'IA',
  deploy_hosting: 'Deploy',
  viral_hooks: 'Viral',
  funnel_conversion: 'Conversión',
  stealth_antibot: 'Stealth',
  reverse_engineering: 'Research',
  ron_mode: 'Modo Ron',
  tools_engineering: 'Herramientas',
};

const JOB_LABELS: Record<string, string> = {
  starting: 'Iniciando Chrome…',
  browser_open: 'Chrome abierto',
  awaiting_login: 'Esperando inicio de sesión…',
  logged_in: 'Sesión detectada',
  harvesting: 'Verificando la cuenta…',
  connected: 'Cuenta verificada',
  logged_in_no_token: 'Sesión sin token',
  failed: 'La conexión falló',
  timeout: 'Tiempo de espera agotado',
  stopped: 'Conexión detenida',
  idle: 'Sin actividad',
};

export type StatusTone = 'ok' | 'fail' | 'idle';

export const STATUS_LABELS: Record<StatusTone, string> = {
  ok: 'Conectado',
  fail: 'Falla',
  idle: 'Sin verificar',
};

export const shortName = (connector: ConnectorCard) =>
  SHORT_NAMES[connector.connector_id] ?? connector.name.replace(/\s*\(.*\)\s*$/, '').trim();

export const subtitle = (connector: ConnectorCard) =>
  SUBTITLES[connector.connector_id] || connector.account_label;

export const statusTone = (status?: string): StatusTone =>
  status === 'CONECTADO' ? 'ok' : status === 'FALLA' ? 'fail' : 'idle';

export const categoryLabel = (key: string) => CATEGORY_LABELS[key] ?? key.replace(/_/g, ' ');

export const jobLabel = (status?: string) => (status ? JOB_LABELS[status] ?? status : '');

export const isBusyJob = (status?: string) =>
  !!status && ['starting', 'browser_open', 'awaiting_login', 'logged_in', 'harvesting'].includes(status);

export const formatMs = (ms?: number | null) =>
  typeof ms === 'number' && ms > 0 ? `${Math.round(ms).toLocaleString('es-CO')} ms` : '—';

export const formatTime = (iso?: string) => {
  if (!iso) return '—';
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return '—';
  return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
};
