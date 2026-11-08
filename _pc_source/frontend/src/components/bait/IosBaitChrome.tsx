import React from 'react';

/**
 * Chrome compartido de las capturas iPhone 15 Pro (393x852 pt).
 * Medidas tomadas de la captura aprobada ios_v2.png y de
 * backend/services/ios_lockscreen_css.py. Sin emojis: solo SVG.
 */

export const BATTERY_LEVEL = 78;

const GRAIN =
  "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 200'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E";

const SignalIcon: React.FC = () => (
  <svg aria-hidden="true" className="block h-[12px] w-[18px] fill-white" viewBox="0 0 18 12">
    <rect x="0" y="8" width="3" height="4" rx="1" />
    <rect x="5" y="5.6" width="3" height="6.4" rx="1" />
    <rect x="10" y="3.2" width="3" height="8.8" rx="1" />
    <rect x="15" y="0" width="3" height="12" rx="1" />
  </svg>
);

const WifiIcon: React.FC = () => (
  <svg aria-hidden="true" className="block h-[12px] w-[17px] fill-white" viewBox="0 0 17 12">
    <path d="M8.5 11.2 6.2 8.6a3.4 3.4 0 0 1 4.6 0L8.5 11.2Z" />
    <path d="M4.6 7a5.9 5.9 0 0 1 7.8 0l-1.3 1.5a3.9 3.9 0 0 0-5.2 0L4.6 7Z" />
    <path d="M1.7 3.9a10.2 10.2 0 0 1 13.6 0l-1.4 1.6a8.1 8.1 0 0 0-10.8 0L1.7 3.9Z" />
  </svg>
);

const BatteryIcon: React.FC<{ level: number }> = ({ level }) => (
  <div
    className="relative ml-px flex h-[13px] w-[27px] items-center justify-center rounded-[4px]"
    style={{ background: 'rgba(255,255,255,.92)' }}
  >
    <span className="text-[9.5px] font-bold leading-none tracking-[-0.3px] text-black">{level}</span>
    <span
      className="absolute -right-[2.5px] top-[4px] h-[5px] w-[1.8px] rounded-r-[2px]"
      style={{ background: 'rgba(255,255,255,.55)' }}
    />
  </div>
);

export const IosStatusBar: React.FC<{ label: string; batteryLevel?: number }> = ({
  label,
  batteryLevel = BATTERY_LEVEL,
}) => (
  <div className="relative z-30 flex h-[54px] shrink-0 items-start justify-between pl-[26px] pr-[26px] pt-[16px]">
    <span className="text-[16px] font-semibold tracking-[-0.2px]" style={{ color: 'rgba(255,255,255,.96)' }}>
      {label}
    </span>
    <div className="flex items-center gap-[5px]">
      <SignalIcon />
      <WifiIcon />
      <BatteryIcon level={batteryLevel} />
    </div>
  </div>
);

const ActionCircle: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div
    className="flex h-[72px] w-[72px] items-center justify-center rounded-full border-[0.5px]"
    style={{
      background: 'rgba(22,24,32,.46)',
      borderColor: 'rgba(255,255,255,.16)',
      backdropFilter: 'blur(24px)',
      WebkitBackdropFilter: 'blur(24px)',
    }}
  >
    {children}
  </div>
);

export const IosBottomActions: React.FC = () => (
  <div className="relative z-30 flex shrink-0 items-center justify-between pl-[30px] pr-[30px] pb-[16px] pt-[4px]">
    <ActionCircle>
      <svg aria-hidden="true" className="h-[27px] w-[27px] fill-white" viewBox="0 0 24 24">
        <path d="M7 3h10a1 1 0 0 1 1 1v2.4a2 2 0 0 1-.6 1.4L15.6 9.7V20a2 2 0 0 1-2 2h-3.2a2 2 0 0 1-2-2V9.7L6.6 7.8A2 2 0 0 1 6 6.4V4a1 1 0 0 1 1-1Zm5 7.2a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3Z" />
      </svg>
    </ActionCircle>
    <ActionCircle>
      <svg aria-hidden="true" className="h-[27px] w-[27px] fill-white" viewBox="0 0 24 24">
        <path d="M8.5 3.5a1.5 1.5 0 0 1 1.2-.6h4.6a1.5 1.5 0 0 1 1.2.6L16.6 5H19a3 3 0 0 1 3 3v10a3 3 0 0 1-3 3H5a3 3 0 0 1-3-3V8a3 3 0 0 1 3-3h2.4l1.1-1.5ZM12 9a4.5 4.5 0 1 0 0 9 4.5 4.5 0 0 0 0-9Zm0 2a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5Z" />
      </svg>
    </ActionCircle>
  </div>
);

export const IosHomeIndicator: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div
    className={`relative z-30 mx-auto h-[5px] w-[134px] shrink-0 rounded-full ${className}`}
    style={{ background: 'rgba(255,255,255,.96)' }}
  />
);

export const IosGrain: React.FC = () => (
  <div
    aria-hidden="true"
    className="pointer-events-none absolute inset-0 z-40 opacity-[0.055] mix-blend-overlay"
    style={{ backgroundImage: `url("${GRAIN}")` }}
  />
);
