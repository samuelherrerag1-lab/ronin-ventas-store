/** Portapapeles seguro: funciona en HTTP LAN donde navigator.clipboard no existe. */

function legacyCopy(text: string): boolean {
  try {
    const area = document.createElement('textarea');
    area.value = text;
    area.setAttribute('readonly', '');
    area.style.position = 'fixed';
    area.style.top = '-9999px';
    area.style.opacity = '0';
    document.body.appendChild(area);
    area.select();
    const ok = document.execCommand('copy');
    document.body.removeChild(area);
    return ok;
  } catch {
    return false;
  }
}

/**
 * Copia texto y devuelve true/false. `navigator.clipboard` requiere contexto
 * seguro; en la LAN por HTTP se usa el fallback con execCommand.
 */
export async function copyText(text: string): Promise<boolean> {
  if (!text) return false;
  if (typeof navigator !== 'undefined' && navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      // cae al fallback
    }
  }
  return legacyCopy(text);
}

/** Copia texto y ejecuta el callback con el resultado, sin promesas colgadas. */
export function copyWithFeedback(text: string, onResult?: (ok: boolean) => void): void {
  void copyText(text).then((ok) => onResult?.(ok));
}
