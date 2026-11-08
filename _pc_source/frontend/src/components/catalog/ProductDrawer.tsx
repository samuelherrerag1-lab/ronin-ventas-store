import React, { useEffect, useRef } from 'react';
import { Icon } from '../ui/Icon';
import { num, usd } from '../../utils/format';
import type { ProductSKU } from '../../types/domain';
import { CoverArt } from './CoverArt';
import { FLAGSHIP, FORMAT_META, NICHE_META } from './catalogMeta';

interface Props {
  sku: ProductSKU;
  onClose: () => void;
  onOpenDeliverable: () => void;
  onToggleStan: () => void;
  onCopyRoute: () => void;
  copied: boolean;
  busy: boolean;
}

const Row: React.FC<{ label: string; children: React.ReactNode }> = ({ label, children }) => (
  <div className="flex items-start justify-between gap-3 border-b border-line py-2 last:border-0">
    <span className="shrink-0 text-[10.5px] text-ink3">{label}</span>
    <span className="min-w-0 text-right text-[11.5px] text-ink2">{children}</span>
  </div>
);

/** Drawer de detalle: portada, ruta, checkout y acceso al visor HTML. */
export const ProductDrawer: React.FC<Props> = ({ sku, onClose, onOpenDeliverable, onToggleStan, onCopyRoute, copied, busy }) => {
  const dialogRef = useRef<HTMLElement>(null);

  useEffect(() => {
    dialogRef.current?.focus();
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [onClose]);

  const format = FORMAT_META[sku.format];
  const niche = NICHE_META[sku.niche];

  return (
    <div className="fixed inset-0 z-[60] flex justify-end" role="presentation">
      <div className="absolute inset-0 bg-black/60" onClick={onClose} />
      <aside
        ref={dialogRef}
        tabIndex={-1}
        role="dialog"
        aria-modal="true"
        aria-label={`${sku.sku_id} — ${sku.title}`}
        className="animate-drawer relative flex h-full w-full max-w-[470px] flex-col border-l border-line2 bg-[#0d0d10] shadow-[0_0_80px_rgba(0,0,0,0.7)] outline-none"
      >
        <header className="flex h-[54px] shrink-0 items-center justify-between gap-2 border-b border-line px-4">
          <div className="flex min-w-0 items-center gap-2">
            <span className="mono-id text-ink3">{sku.sku_id}</span>
            <span className="chip border-transparent bg-panel3 px-1.5 text-[9.5px]">{format?.short ?? sku.format}</span>
            {FLAGSHIP.has(sku.sku_id) && <span className="chip border-transparent bg-accent/10 px-1.5 text-[9px] text-accent">flagship</span>}
          </div>
          <button type="button" onClick={onClose} aria-label="Cerrar detalle" className="btn btn-ghost btn-icon">
            <Icon name="close" size={16} />
          </button>
        </header>

        <div className="scroll-thin flex-1 px-4 py-3.5">
          <div className="flex gap-3.5">
            <CoverArt skuId={sku.sku_id} title={sku.title} className="w-[104px] shrink-0" />
            <div className="min-w-0 flex-1">
              <h2 className="font-display text-[16px] leading-tight text-ink">{sku.title}</h2>
              <p className="mt-1.5 text-[11px] leading-relaxed text-ink3">{sku.subtitle}</p>
              <div className="mt-2 flex items-baseline gap-1.5">
                <span className="num text-[20px] leading-none text-ink">{sku.price_usd === 0 ? 'Gratis' : usd(sku.price_usd, 0)}</span>
                {sku.price_usd > 0 && <span className="unit">USD · {num(sku.price_cop)} COP</span>}
              </div>
            </div>
          </div>

          <div className="mt-4">
            <Row label="Nicho">{niche?.label ?? sku.niche}</Row>
            <Row label="Formato">{format?.label ?? sku.format}</Row>
            <Row label="Gancho">
              <span className="italic">“{sku.hook_angle}”</span>
            </Row>
            <Row label="Ruta puente">
              <span className="flex items-center justify-end gap-1.5">
                <span className="mono-id truncate text-accent">{sku.bridge_route}</span>
                <button type="button" onClick={onCopyRoute} aria-label="Copiar ruta puente" className="btn btn-ghost btn-icon h-6 w-6">
                  <Icon name={copied ? 'check' : 'copy'} size={12} className={copied ? 'text-pos' : 'text-ink3'} />
                </button>
              </span>
            </Row>
            <Row label="Checkout">
              <span className="flex items-center justify-end gap-1.5">
                <span className={`chip border-transparent px-1.5 text-[9.5px] ${sku.checkout_ready ? 'bg-pos/10 text-pos' : 'bg-warn/10 text-warn'}`}>
                  {sku.checkout_ready ? 'listo' : 'sin URL'}
                </span>
                <span className="text-[10px] text-ink3">{sku.gumroad_url ? 'Gumroad' : ''}{sku.gumroad_url && sku.hotmart_url ? ' · ' : ''}{sku.hotmart_url ? 'Hotmart' : ''}</span>
              </span>
            </Row>
            <Row label="Estado">{sku.status === 'published' ? 'publicado' : sku.status === 'generated' ? 'generado' : 'spec lista'}</Row>
          </div>

          <div className="mt-3 rounded-ctl border border-line bg-panel px-3 py-2.5">
            <p className="text-[9.5px] text-ink3">Entregable</p>
            <p className="mt-1 text-[11px] leading-relaxed text-ink2">{sku.deliverable_spec}</p>
          </div>
        </div>

        <footer className="shrink-0 space-y-1.5 border-t border-line p-3">
          <div className="flex gap-1.5">
            <button type="button" onClick={onOpenDeliverable} disabled={busy} className="btn btn-primary flex-1">
              <Icon name="play" size={13} />
              {busy ? 'Generando…' : 'Vista HTML'}
            </button>
            <button type="button" onClick={onCopyRoute} className="btn">
              <Icon name={copied ? 'check' : 'copy'} size={13} className={copied ? 'text-pos' : ''} />
              Ruta
            </button>
            <button
              type="button"
              onClick={onToggleStan}
              aria-pressed={sku.featured_on_stan}
              className={`btn ${sku.featured_on_stan ? 'border-warn/40 text-warn' : ''}`}
            >
              <Icon name="box" size={13} />
              {sku.featured_on_stan ? 'En Stan' : 'A Stan'}
            </button>
          </div>
          <p className="text-center text-[9px] text-ink3">El visor abre el entregable real servido por el backend.</p>
        </footer>
      </aside>
    </div>
  );
};

/** Visor del entregable HTML en pantalla completa. */
export const DeliverableModal: React.FC<{ title: string; skuId: string; url: string; onClose: () => void }> = ({ title, skuId, url, onClose }) => {
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-[70] flex items-center justify-center bg-black/75 p-2 sm:p-4" role="presentation" onClick={onClose}>
      <div
        role="dialog"
        aria-modal="true"
        aria-label={`Entregable ${skuId}`}
        onClick={(event) => event.stopPropagation()}
        className="flex h-[88vh] w-full max-w-[1080px] flex-col overflow-hidden rounded-xl border border-line2 bg-[#0d0d10]"
      >
        <header className="flex h-11 shrink-0 items-center justify-between gap-2 border-b border-line px-3">
          <div className="flex min-w-0 items-center gap-2">
            <span className="mono-id text-ink3">{skuId}</span>
            <span className="truncate text-[12px] text-ink">{title}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <a href={url} target="_blank" rel="noreferrer" className="btn btn-sm">
              <Icon name="external" size={12} />
              Pestaña
            </a>
            <button type="button" onClick={onClose} aria-label="Cerrar visor" className="btn btn-ghost btn-icon">
              <Icon name="close" size={15} />
            </button>
          </div>
        </header>
        <iframe src={url} title={title} className="h-full w-full flex-1 bg-black" />
      </div>
    </div>
  );
};
