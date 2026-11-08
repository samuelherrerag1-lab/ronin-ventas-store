import React, { useEffect, useState } from 'react';
import { BrandMark } from '../ui/BrandMark';
import { Icon } from '../ui/Icon';
import { MOBILE_PRIMARY, NAV_BY_ID, NAV_ITEMS, type NavTabId } from './nav';

interface Props {
  activeTab: NavTabId;
  onSelectTab: (tab: NavTabId) => void;
  onOpenLan: () => void;
  onOpenPalette: () => void;
  onRefresh: () => void;
  lanUrl: string;
}

/** Dock inferior glass: 4 destinos de trabajo + hoja "Más" con el resto. */
export const MobileDock: React.FC<Props> = ({ activeTab, onSelectTab, onOpenLan, onOpenPalette, onRefresh, lanUrl }) => {
  const [open, setOpen] = useState(false);
  const rest = NAV_ITEMS.filter((item) => !MOBILE_PRIMARY.includes(item.id));

  useEffect(() => {
    if (!open) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setOpen(false);
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [open]);

  const select = (tab: NavTabId) => {
    onSelectTab(tab);
    setOpen(false);
  };

  return (
    <>
      {open && (
        <div className="fixed inset-0 z-40 lg:hidden" role="presentation">
          <div className="absolute inset-0 bg-black/60" onClick={() => setOpen(false)} />
          <div
            role="dialog"
            aria-modal="true"
            aria-label="Más destinos"
            className="glass-sheet animate-sheet absolute inset-x-0 bottom-0 rounded-t-2xl px-3 pb-[calc(env(safe-area-inset-bottom)+12px)] pt-2"
          >
            <div className="mx-auto mb-2 h-1 w-10 rounded-full bg-line2" aria-hidden="true" />
            <div className="grid grid-cols-2 gap-1.5">
              {rest.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => select(item.id)}
                  className={`flex h-11 items-center gap-2.5 rounded-ctl border px-3 text-[12.5px] ${
                    activeTab === item.id ? 'border-line2 bg-panel2 text-ink' : 'border-line bg-panel/60 text-ink2'
                  }`}
                >
                  <Icon name={item.icon} size={16} className={activeTab === item.id ? 'text-accent' : 'text-ink3'} />
                  {item.label}
                </button>
              ))}
            </div>
            <div className="mt-2 grid grid-cols-3 gap-1.5">
              <button type="button" onClick={() => { onOpenPalette(); setOpen(false); }} className="btn h-10 justify-center text-[11.5px]">
                <Icon name="search" size={14} /> Buscar
              </button>
              <button type="button" onClick={() => { onRefresh(); setOpen(false); }} className="btn h-10 justify-center text-[11.5px]">
                <Icon name="refresh" size={14} /> Sincronizar
              </button>
              <button type="button" onClick={() => { onOpenLan(); setOpen(false); }} className="btn h-10 justify-center text-[11.5px]">
                <Icon name="wifi" size={14} className={lanUrl ? 'text-pos' : 'text-ink3'} /> LAN
              </button>
            </div>
          </div>
        </div>
      )}

      <nav
        className="glass-dock fixed inset-x-0 bottom-0 z-40 grid grid-cols-5 items-end gap-0 px-1 pb-[calc(env(safe-area-inset-bottom)+4px)] pt-1 lg:hidden"
        aria-label="Navegación móvil"
      >
        {MOBILE_PRIMARY.map((id) => {
          const item = NAV_BY_ID[id];
          const active = activeTab === id;
          return (
            <button
              key={id}
              type="button"
              onClick={() => onSelectTab(id)}
              aria-current={active ? 'page' : undefined}
              className="flex h-[46px] flex-col items-center justify-center gap-0.5 rounded-ctl"
            >
              <span className={active ? 'text-accent' : 'text-ink3'}>
                <Icon name={item.icon} size={19} strokeWidth={active ? 2 : 1.7} />
              </span>
              <span className={`text-[9.5px] leading-none ${active ? 'font-medium text-ink' : 'text-ink3'}`}>{item.short}</span>
            </button>
          );
        })}
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          aria-expanded={open}
          aria-label="Más destinos"
          className="flex h-[46px] flex-col items-center justify-center gap-0.5 rounded-ctl"
        >
          <span className={open ? 'text-accent' : 'text-ink3'}>
            <Icon name="more" size={19} />
          </span>
          <span className={`text-[9.5px] leading-none ${open ? 'font-medium text-ink' : 'text-ink3'}`}>Más</span>
        </button>
      </nav>
    </>
  );
};

export const MobileBrand: React.FC = () => (
  <span className="flex items-center gap-2">
    <BrandMark size={20} className="text-ink" />
    <span className="font-display text-[12.5px] font-bold tracking-[-0.02em] text-ink">Ronin OS</span>
  </span>
);
