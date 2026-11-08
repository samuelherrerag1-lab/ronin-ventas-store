/**
 * Error uniforme de la API. `pending` marca endpoints que todavía no existen en
 * el backend (404/503 o HTML del catch-all SPA). La UI muestra "Pendiente en
 * backend" en ese caso, en lugar de romperse o fingir datos.
 */
export class ApiError extends Error {
  readonly status: number;
  readonly path: string;
  readonly detail: string;
  readonly pending: boolean;

  constructor(path: string, status: number, detail: string, pending = false) {
    super(`API [${status}] ${path}: ${detail}`);
    this.name = 'ApiError';
    this.path = path;
    this.status = status;
    this.detail = detail;
    this.pending = pending;
  }
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}

export function isPendingError(error: unknown): boolean {
  return isApiError(error) && error.pending;
}

export function errorMessage(error: unknown): string {
  if (isApiError(error)) return error.detail;
  if (error instanceof Error) return error.message;
  return String(error);
}

/** Extrae el `detail` legible de una respuesta de error (JSON FastAPI o HTML). */
export function extractErrorDetail(body: string, isJson: boolean): string {
  if (!isJson) return body.slice(0, 180);
  try {
    const parsed = JSON.parse(body) as { detail?: unknown };
    if (typeof parsed.detail === 'string') return parsed.detail;
    if (parsed.detail !== undefined) return JSON.stringify(parsed.detail);
    return body;
  } catch {
    return body.slice(0, 180);
  }
}
