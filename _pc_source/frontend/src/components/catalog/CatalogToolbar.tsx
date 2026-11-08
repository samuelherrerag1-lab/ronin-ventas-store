import React from 'react';
import { Icon } from '../ui/Icon';
import { Segmented } from '../ui/primitives';
import { num } from '../../utils/format';
import type { ProductSKU } from '../../types/domain';
import { FLAGSHIP, FORMAT_META, FORMAT_ORDER, NICHE_META, PRICE_BANDS, formatCount } from './catalogMeta';

export interface CatalogFilters {
  search: string;
  format: string;
  niche: string;
  price: string;
  checkoutOnly: boolean;
  flagshipOnly: boolean;
  view: 'grid' | 'list';
}

interface Props {
  filters: CatalogFilters;
  onChange: (patch: Partial<CatalogFilters>) => void;
  products: ProductSKU[];
  shown: number;
}

/** Barra de filtros del arsenal: búsqueda, formato, nicho, precio y checkout. */
export const CatalogToolbar: React.FC<Props> = ({ filters, onChange, products, shown }) => (
  <div className="space-y-2">
    <div className="flex flex-wrap items-center gap-2">
      <label className="relative min-w-0 flex-1 sm:max-w-[280px]">
        <Icon name="search" size={14} className="pointer-events-none absolute left-2.5 top-1/2 -translate-y-1/2 text-ink3" />
        <input
          type="search"
          value={filters.search}
          onChange={(event) => onChange({ search: event.target.value })}
          placeholder="ID, título o gancho"
          aria-label="Buscar SKU por ID, título o gancho"
          className="field w-full pl-8"
        />
      </label>

      <label className="flex items-center gap-1.5">
        <span className="text-[10.5px] text-ink3">Nicho</span>
        <select className="field max-w-[150px]" value={filters.niche} onChange={(event) => onChange({ niche: event.target.value })} aria-label="Filtrar por nicho">
          <option value="all">Todos</option>
          {Object.entries(NICHE_META).map(([key, meta]) => (
            <option key={key} value={key}>{meta.short}</option>
          ))}
        </select>
      </label>

      <Segmented ariaLabel="Rango de precio" value={filters.price} onChange={(value) => onChange({ price: value })} options={PRICE_BANDS} />

      <div className="ml-auto flex items-center gap-1.5">
        <span className="text-[10.5px] text-ink3">
          <span className="num text-ink2">{shown}</span> / {products.length}
        </span>
        <div className="seg" role="group" aria-label="Vista">
          <button type="button" aria-pressed={filters.view === 'grid'} aria-label="Vista de cuadrícula" onClick={() => onChange({ view: 'grid' })}>
            <Icon name="grid" size={13} />
          </button>
          <button type="button" aria-pressed={filters.view === 'list'} aria-label="Vista de lista" onClick={() => onChange({ view: 'list' })}>
            <Icon name="list" size={13} />
          </button>
        </div>
      </div>
    </div>

    <div className="space-y-1.5">
      <div className="no-scrollbar -mx-1 flex items-center gap-1.5 overflow-x-auto px-1 sm:flex-wrap sm:overflow-visible">
        <button
          type="button"
          onClick={() => onChange({ format: 'all' })}
          aria-pressed={filters.format === 'all'}
          className={`chip shrink-0 transition-colors duration-150 ${filters.format === 'all' ? 'border-line2 bg-panel3 text-ink' : 'hover:text-ink'}`}
        >
          Todos <span className="num text-ink3">{products.length}</span>
        </button>
        {FORMAT_ORDER.map((format) => {
          const count = formatCount(products, format);
          const on = filters.format === format;
          return (
            <button
              key={format}
              type="button"
              onClick={() => onChange({ format })}
              aria-pressed={on}
              className={`chip shrink-0 transition-colors duration-150 ${on ? 'border-line2 bg-panel3 text-ink' : 'hover:text-ink'} ${
                count === 0 ? 'opacity-40' : ''
              }`}
            >
              {FORMAT_META[format].short} <span className="num text-ink3">{count}</span>
            </button>
          );
        })}
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <label className="flex items-center gap-1.5">
          <span className="text-[10.5px] text-ink3">Solo con checkout</span>
          <button
            type="button"
            role="switch"
            aria-checked={filters.checkoutOnly}
            aria-label="Solo SKU con checkout configurado"
            onClick={() => onChange({ checkoutOnly: !filters.checkoutOnly })}
            className="switch scale-[0.86]"
          />
        </label>
        <button
          type="button"
          onClick={() => onChange({ flagshipOnly: !filters.flagshipOnly })}
          aria-pressed={filters.flagshipOnly}
          className={`chip transition-colors duration-150 ${filters.flagshipOnly ? 'border-accent/40 bg-accent/10 text-accent' : 'hover:text-ink'}`}
        >
          <Icon name="bolt" size={10} />
          Flagship <span className="num">{products.filter((p) => FLAGSHIP.has(p.sku_id)).length}</span>
        </button>
        <span className="ml-auto hidden text-[10px] text-ink3 md:block">
          rutas únicas <span className="num text-ink2">{num(new Set(products.map((p) => p.bridge_route)).size)}</span>
        </span>
      </div>
    </div>
  </div>
);
