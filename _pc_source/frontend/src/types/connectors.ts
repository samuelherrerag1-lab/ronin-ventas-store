/** Tipos de conectores/diagnóstico (SSO) usados por el client de API y el Hub. */

export type ConnectorStatus = 'CONECTADO' | 'FALLA' | 'SIN_VERIFICAR';

export interface ConnectorTestResult {
  connector_id: string;
  name: string;
  status: ConnectorStatus;
  latency_ms: number;
  detail: string;
  checked_at: string;
  error_literal?: string;
}

export interface TestAllResponse {
  total: number;
  connected_count: number;
  falla_count: number;
  sin_verificar_count: number;
  results: Record<string, ConnectorTestResult>;
  tested_at: string;
}

export type ConnectJobStatus =
  | 'starting'
  | 'browser_open'
  | 'awaiting_login'
  | 'logged_in'
  | 'harvesting'
  | 'connected'
  | 'logged_in_no_token'
  | 'failed'
  | 'timeout'
  | 'stopped'
  | 'idle'
  | (string & {});

export interface ConnectJob {
  connector_id: string;
  status: ConnectJobStatus;
  step?: string;
  detail?: string | null;
  evidence?: string | null;
  elapsed_sec?: number;
  updated_at?: string;
}
