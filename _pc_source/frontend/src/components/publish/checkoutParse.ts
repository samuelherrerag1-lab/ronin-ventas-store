import type { CheckoutBulkLink } from '../../types/domain';

export interface ParsedCheckoutLinks {
  links: Record<string, CheckoutBulkLink>;
  errors: string[];
}

const SKU_RE = /^[A-Za-z]\d{2}$/;

function classifyUrl(raw: string): 'gumroad' | 'hotmart' | null {
  const value = raw.trim().toLowerCase();
  if (!value) return null;
  if (value.includes('gumroad.com')) return 'gumroad';
  if (value.includes('hotmart.com')) return 'hotmart';
  return null;
}

/** Valida una URL de checkout: https obligatorio y host de la pasarela. */
export function validateCheckoutUrl(raw: string, kind: 'gumroad' | 'hotmart'): string | null {
  const value = raw.trim();
  if (!value) return null;
  if (!/^https:\/\//i.test(value)) return 'La URL debe empezar por https://';
  let host: string;
  try {
    host = new URL(value).hostname.toLowerCase();
  } catch {
    return 'URL inválida.';
  }
  const root = `${kind}.com`;
  const ok = host === root || host.endsWith(`.${root}`);
  return ok ? null : `El host "${host}" no pertenece a ${root}.`;
}


function addLink(
  links: Record<string, CheckoutBulkLink>,
  sku: string,
  gateway: 'gumroad' | 'hotmart',
  url: string
): void {
  const entry = links[sku] ?? {};
  entry[gateway === 'gumroad' ? 'gumroad_url' : 'hotmart_url'] = url;
  links[sku] = entry;
}

/**
 * Acepta JSON `{ "E01": {"gumroad_url": "...", "hotmart_url": "..."} }`
 * o líneas `SKU,URL` / `SKU,URL_GUMROAD,URL_HOTMART` (el gateway se deduce del host).
 */
export function parseCheckoutLinks(input: string): ParsedCheckoutLinks {
  const links: Record<string, CheckoutBulkLink> = {};
  const errors: string[] = [];
  const trimmed = input.trim();
  if (!trimmed) return { links, errors: ['El bloque está vacío.'] };

  if (trimmed.startsWith('{')) {
    let parsed: unknown;
    try {
      parsed = JSON.parse(trimmed);
    } catch (error) {
      return { links, errors: [`JSON inválido: ${(error as Error).message}`] };
    }
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
      return { links, errors: ['El JSON debe ser un objeto { "E01": { ... } }.'] };
    }
    Object.entries(parsed as Record<string, unknown>).forEach(([rawSku, value]) => {
      const sku = rawSku.trim().toUpperCase();
      if (!SKU_RE.test(sku)) {
        errors.push(`SKU inválido en JSON: "${rawSku}" (formato esperado E01, B03...).`);
        return;
      }
      if (!value || typeof value !== 'object') {
        errors.push(`${sku}: el valor debe ser un objeto con gumroad_url/hotmart_url.`);
        return;
      }
      const entry = value as Record<string, unknown>;
      const gumroad = typeof entry.gumroad_url === 'string' ? entry.gumroad_url.trim() : '';
      const hotmart = typeof entry.hotmart_url === 'string' ? entry.hotmart_url.trim() : '';
      if (!gumroad && !hotmart) {
        errors.push(`${sku}: sin URLs (usa cadena vacía para borrar un link existente).`);
        return;
      }
      links[sku] = {};
      if (gumroad) links[sku].gumroad_url = gumroad;
      if (hotmart) links[sku].hotmart_url = hotmart;
    });
    return { links, errors };
  }

  trimmed.split(/\r?\n/).forEach((line, index) => {
    const clean = line.trim();
    if (!clean || clean.startsWith('#')) return;
    const parts = clean.split(',').map((p) => p.trim());
    const sku = parts[0]?.toUpperCase() ?? '';
    if (!SKU_RE.test(sku)) {
      errors.push(`Línea ${index + 1}: SKU inválido "${parts[0] ?? ''}".`);
      return;
    }
    const urls = parts.slice(1).filter(Boolean);
    if (urls.length === 0) {
      errors.push(`Línea ${index + 1} (${sku}): falta la URL.`);
      return;
    }
    urls.forEach((url) => {
      const gateway = classifyUrl(url);
      if (!gateway) {
        errors.push(`Línea ${index + 1} (${sku}): la URL no es de gumroad.com ni hotmart.com.`);
        return;
      }
      addLink(links, sku, gateway, url);
    });
  });

  if (Object.keys(links).length === 0 && errors.length === 0) {
    errors.push('No se detectó ninguna línea "SKU,URL".');
  }
  return { links, errors };
}
