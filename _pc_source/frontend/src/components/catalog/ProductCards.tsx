import React from 'react';
import { Icon } from '../ui/Icon';
import { Tip } from '../ui/Tooltip';
import { num } from '../../utils/format';
import type { ProductSKU } from '../../types/domain';
import { CoverArt } from './CoverArt';
import { FLAGSHIP, FORMAT_META } from './catalogMeta';

interface Props {
  sku: ProductSKU;
  onOpen: () => void;
  onCopyRoute: () => void;
  copied: boolean;
}

/** Tarjeta del catálogo: portada, id, formato, precio y estado de checkout en 110px. */
export const ProductCard: React.FC<Props> = ({ sku, onOpen, onCopyRoute, copied }) => {
  const free = sku.price_usd === 0;
  const format = FORMAT_META[sku.format];
  return (
    <article className="panel group relative flex flex-col overflow-hidden transition-colors duration-150 hover:border-line2">
      <button type="button" onClick={onOpen} className="flex flex-1 gap-3 p-3 text-left" aria-label={`Ver detalle de ${sku.title}`}>
        <CoverArt skuId={sku.sku_id} title={sku.title} className="w-[48px] shrink-0" />
        <span className="min-w-0 flex-1">
          <span className="flex items-center gap-1.5">
            <span className="mono-id text-ink3">{sku.sku_id}</span>
            {FLAGSHIP.has(sku.sku_id) && <span className="chip border-transparent bg-accent/10 px-1 text-[9px] text-accent">flagship</span>}
            <span className="ml-auto shrink-0 text-[9.5px] text-ink3">{format?.short ?? sku.format}</span>
          </span>
          <span className="mt-1 line-clamp-2 block text-[12.5px] font-medium leading-snug text-ink">{sku.title}</span>
          <span className="mt-1 line-clamp-1 block text-[10.5px] leading-snug text-ink3">{sku.hook_angle}</span>
        </span>
      </button>
      <div className="mt-auto flex items-center justify-between gap-2 border-t border-line px-3 py-2">
        <span className="flex items-baseline gap-1">
          <span className="num text-[14.5px] text-ink">{free ? 'Gratis' : `$${num(sku.price_usd, 0)}`}</span>
          {!free && <span className="unit">USD</span>}
        </span>
        <span className="flex items-center gap-1">
          <Tip side="top" label={sku.checkout_ready ? 'Gumroad u Hotmart con URL lista' : 'Sin URL de checkout: pendiente de configurar'}>
            <span className={`chip border-transparent px-1.5 text-[9.5px] ${sku.checkout_ready ? 'bg-pos/10 text-pos' : 'bg-warn/10 text-warn'}`}>
              {sku.checkout_ready ? 'checkout' : 'pendiente'}
            </span>
          </Tip>
          <button
            type="button"
            onClick={onCopyRoute}
            aria-label={`Copiar ruta de ${sku.sku_id}`}
            className="btn btn-ghost btn-icon h-6 w-6"
          >
            <Icon name={copied ? 'check' : 'copy'} size={12} className={copied ? 'text-pos' : 'text-ink3'} />
          </button>
        </span>
      </div>
    </article>
  );
};

/** Fila compacta para la vista de lista densa. */
export const ProductRow: React.FC<Props> = ({ sku, onOpen, onCopyRoute, copied }) => {
  const free = sku.price_usd === 0;
  return (
    <div className="group flex items-center gap-3 border-b border-line px-3 py-2 transition-colors duration-150 last:border-0 hover:bg-panel2/60">
      <CoverArt skuId={sku.sku_id} title={sku.title} className="w-[28px] shrink-0" />
      <button type="button" onClick={onOpen} className="flex min-w-0 flex-1 items-center gap-3 text-left" aria-label={`Ver detalle de ${sku.title}`}>
        <span className="mono-id w-[34px] shrink-0 text-ink3">{sku.sku_id}</span>
        <span className="min-w-0 flex-1">
          <span className="block truncate text-[12px] text-ink">{sku.title}</span>
          <span className="block truncate text-[10px] text-ink3">{sku.hook_angle}</span>
        </span>
        <span className="hidden w-[84px] shrink-0 text-[10.5px] text-ink3 md:block">{FORMAT_META[sku.format]?.short}</span>
        <span className="mono-id hidden w-[180px] shrink-0 truncate text-ink3 lg:block">{sku.bridge_route}</span>
      </button>
      <span className="num w-[64px] shrink-0 text-right text-[12px] text-ink">{free ? 'Gratis' : `$${num(sku.price_usd, 0)}`}</span>
      <span className={`chip w-[74px] shrink-0 justify-center border-transparent px-1 text-[9px] ${sku.checkout_ready ? 'bg-pos/10 text-pos' : 'bg-warn/10 text-warn'}`}>
        {sku.checkout_ready ? 'listo' : 'pendiente'}
      </span>
      <button type="button" onClick={onCopyRoute} aria-label={`Copiar ruta de ${sku.sku_id}`} className="btn btn-ghost btn-icon h-6 w-6 shrink-0">
        <Icon name={copied ? 'check' : 'copy'} size={12} className={copied ? 'text-pos' : 'text-ink3'} />
      </button>
    </div>
  );
};
