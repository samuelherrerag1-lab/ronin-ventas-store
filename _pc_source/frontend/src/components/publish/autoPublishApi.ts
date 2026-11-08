import { request } from '../../api/client';

/**
 * Cliente del publicador social real (`backend/routers/api_social_publish.py`).
 * Si el router no está montado todavía, `request` lanza ApiError con
 * `pending=true` y el panel muestra "Pendiente en backend" sin romperse.
 */

export type SocialPlatform = 'threads' | 'pinterest';

export interface SocialSessionState {
  platform: string;
  logged_in: boolean;
  status: string;
  account_label: string | null;
  evidence: string;
  checked_at: string | null;
  url?: string | null;
  screenshot?: string | null;
  stale?: boolean;
  age_seconds?: number | null;
  measured?: boolean;
}

export interface SocialProfileInfo {
  path: string;
  channel: string;
  is_vault: boolean;
  in_use_by: string | null;
  browser_busy: boolean;
}

export interface SocialJobProgress {
  total: number;
  done: number;
  ok: number;
  failed: number;
}

export interface SocialJobPiece {
  id: string;
  sku_id?: string | null;
  status: string;
  post_url?: string | null;
  screenshot?: string | null;
  error?: string | null;
  notes?: string[];
  self_replies_scheduled?: number;
}

export interface SocialJobSummary {
  job_id: string;
  platform: string;
  dry_run: boolean;
  status: string;
  progress?: SocialJobProgress;
  error?: string | null;
  published_urls?: Array<string | null>;
  created_at?: string | null;
  finished_at?: string | null;
}

export interface SocialJob extends SocialJobSummary {
  pieces: SocialJobPiece[];
  steps?: Array<{ at: string; name: string; status: string; detail: string }>;
  screenshots?: string[];
  session?: SocialSessionState | null;
}

export interface SocialStatus {
  profile: SocialProfileInfo;
  sessions: Record<string, SocialSessionState>;
  login: { running: boolean; platform: string | null; status: string; detail: string };
  scheduler: { running: boolean; enabled: boolean; dry_run: boolean; next_slot: string | null; pending_replies: number };
  jobs: { total: number; running: SocialJobSummary[]; last: SocialJobSummary | null };
}

export interface SocialQueueItem {
  id: string;
  sku_id: string;
  status: string;
  text: string;
  title?: string | null;
  board?: string | null;
  target_route?: string | null;
  image_url?: string | null;
  has_image: boolean;
  published_url?: string | null;
  notes?: string[];
}

export interface SocialSchedule {
  enabled: boolean;
  dry_run: boolean;
  threads_per_day: number;
  pinterest_per_day: number;
  times_local: string[];
  next_slot?: string | null;
  pending_replies?: number;
  last_error?: string | null;
}

export async function fetchSocialStatus(): Promise<SocialStatus> {
  return request<SocialStatus>('/api/social/status');
}

export async function fetchSocialSession(
  platform: SocialPlatform,
  verify = false
): Promise<SocialSessionState> {
  const suffix = verify ? '?verify=true' : '';
  const res = await request<{ state: SocialSessionState }>(
    `/api/social/session/${platform}${suffix}`
  );
  return { ...res.state, measured: verify || res.state.measured };
}

export async function openSocialLogin(platform: SocialPlatform): Promise<{ detail: string; note: string }> {
  return request(`/api/social/login/${platform}`, { method: 'POST' });
}

export async function fetchSocialQueue(platform: SocialPlatform, limit = 50): Promise<SocialQueueItem[]> {
  const res = await request<{ items: SocialQueueItem[] }>(
    `/api/social/queue?platform=${platform}&limit=${limit}`
  );
  return res.items ?? [];
}

export async function startSocialPublish(payload: {
  platform: SocialPlatform;
  ids: string[];
  limit: number;
  dry_run: boolean;
}): Promise<{ job_id: string; note: string; job: SocialJobSummary }> {
  return request('/api/social/publish', { method: 'POST', body: JSON.stringify(payload) });
}

export async function fetchSocialJob(jobId: string): Promise<SocialJob> {
  const res = await request<{ job: SocialJob }>(`/api/social/jobs/${encodeURIComponent(jobId)}`);
  return res.job;
}

export async function fetchSocialSchedule(): Promise<SocialSchedule> {
  const res = await request<{ schedule: SocialSchedule }>('/api/social/schedule');
  return res.schedule;
}

export async function saveSocialSchedule(payload: Partial<SocialSchedule>): Promise<SocialSchedule> {
  const res = await request<{ schedule: SocialSchedule }>('/api/social/schedule', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return res.schedule;
}
