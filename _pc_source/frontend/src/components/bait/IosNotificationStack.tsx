import React from 'react';

/**
 * Centro de notificaciones iOS 17.5 segun la captura aprobada.
 * Tarjeta de 361 pt, radio 22, blur 34 e iconos de 34 pt.
 */

const DEFAULT_NOTIFICATIONS = ['Gumroad: You made a sale! $27.00 — Bóveda 500 Hooks'];

const isHotmart = (raw: string): boolean => /hotmart|nequi|pse|efecty|cop/i.test(raw);

const cleanBody = (raw: string): string =>
  raw
    .replace(/^(gumroad|hotmart|stripe)\s*[•:\-]?\s*/i, '')
    .replace(/\s+/g, ' ')
    .trim();

interface NotificationModel {
  app: 'Gumroad' | 'Hotmart';
  body: string;
  time: string;
}

const buildModels = (raw: string[]): NotificationModel[] => {
  const unique = Array.from(new Set(raw.map((item) => item.trim()).filter(Boolean)));
  const source = unique.length ? unique : DEFAULT_NOTIFICATIONS;
  return source.slice(0, 2).map((item, index) => ({
    app: isHotmart(item) ? 'Hotmart' : 'Gumroad',
    body: cleanBody(item) || item,
    time: index === 0 ? 'ahora' : `Hace ${index * 9 + 2} min`,
  }));
};

const CloseButton: React.FC = () => (
  <div
    className="flex h-[26px] w-[26px] shrink-0 items-center justify-center rounded-full"
    style={{ background: 'rgba(255,255,255,.22)', backdropFilter: 'blur(12px)', WebkitBackdropFilter: 'blur(12px)' }}
  >
    <svg aria-hidden="true" className="h-[11px] w-[11px] fill-none stroke-white" strokeWidth="2.4" viewBox="0 0 24 24">
      <path d="M5 5l14 14M19 5L5 19" strokeLinecap="round" />
    </svg>
  </div>
);

const AppIcon: React.FC<{ app: 'Gumroad' | 'Hotmart' }> = ({ app }) =>
  app === 'Hotmart' ? (
    <div
      className="flex h-[34px] w-[34px] shrink-0 items-center justify-center rounded-[8.5px]"
      style={{ background: 'linear-gradient(135deg,#FF6A3D 0%,#E83E14 100%)' }}
    >
      <svg aria-hidden="true" className="h-[22px] w-[22px] fill-white" viewBox="0 0 24 24">
        <path d="M12 2C9.5 6 7 9 7 13a5 5 0 0 0 10 0c0-1.5-.5-3-1.5-4.5C14.5 10 13 11.5 13 13a1 1 0 1 1-2 0c0-2.5 2-4.5 3-6-1 0-2.5 1-3.5 2.5C10 8 11 5 12 2Z" />
      </svg>
    </div>
  ) : (
    <div
      className="flex h-[34px] w-[34px] shrink-0 items-center justify-center rounded-[8.5px]"
      style={{ background: '#FF90E8' }}
    >
      <div className="flex h-[23px] w-[23px] items-center justify-center rounded-full bg-black text-[13px] font-black leading-none text-[#FF90E8]">
        G
      </div>
    </div>
  );

const NotificationCard: React.FC<{ model: NotificationModel }> = ({ model }) => (
  <div
    className="mb-[7px] flex items-center gap-[11px] rounded-[22px] border-[0.5px] px-[13px] py-[11px]"
    style={{
      background: 'rgba(24,26,34,.58)',
      borderColor: 'rgba(255,255,255,.14)',
      backdropFilter: 'blur(34px) saturate(180%)',
      WebkitBackdropFilter: 'blur(34px) saturate(180%)',
      boxShadow: '0 12px 34px rgba(0,0,0,.42)',
    }}
  >
    <AppIcon app={model.app} />
    <div className="min-w-0 flex-1">
      <div className="flex items-baseline justify-between gap-2">
        <span className="truncate text-[15px] font-semibold tracking-[-0.15px] text-white">{model.app}</span>
        <span className="shrink-0 text-[11.5px] font-normal" style={{ color: 'rgba(255,255,255,.55)' }}>
          {model.time}
        </span>
      </div>
      <p
        className="mt-px line-clamp-2 text-[14.5px] font-normal leading-[1.2] tracking-[-0.1px]"
        style={{ color: 'rgba(255,255,255,.92)' }}
      >
        {model.body}
      </p>
    </div>
  </div>
);

export const IosNotificationStack: React.FC<{ notifications?: string[] }> = ({ notifications }) => {
  const models = buildModels(notifications?.length ? notifications : DEFAULT_NOTIFICATIONS);
  return (
    <div className="relative z-20 mt-auto mb-[10px] shrink-0 px-[16px]">
      <div className="flex items-center justify-between px-[6px] pb-[8px]">
        <span className="text-[18px] font-semibold tracking-[-0.35px] text-white/[0.96]">Centro de notificaciones</span>
        <CloseButton />
      </div>
      {models.map((model, index) => (
        <NotificationCard key={`${model.app}-${index}`} model={model} />
      ))}
      <div className="-mt-[11px] mx-[14px] h-[9px] rounded-b-[18px]" style={{ background: 'rgba(24,26,34,.4)' }} />
    </div>
  );
};
