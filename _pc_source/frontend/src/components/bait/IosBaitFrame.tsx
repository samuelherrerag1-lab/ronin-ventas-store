import React from 'react';
import type { BaitWidgetConfig } from '../../types/domain';
import { AppleNotesMode, StripeDashboardMode } from './IosSubModes';
import { IosStatusBar, IosBottomActions, IosHomeIndicator, IosGrain } from './IosBaitChrome';
import { IosNotificationStack } from './IosNotificationStack';

const FRAME_WIDTH = 393;
const FRAME_HEIGHT = 852;
const COMPACT_SCALE = 693 / FRAME_HEIGHT;

const FONT_STACK = "'SF Pro Display',-apple-system,BlinkMacSystemFont,'Inter',sans-serif";

const PlayIcon: React.FC = () => (
  <svg aria-hidden="true" className="h-[15px] w-[15px] shrink-0 fill-current opacity-95" viewBox="0 0 24 24">
    <path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm-1.2 5.6 6 4.4-6 4.4V7.6Z" />
  </svg>
);

const NowLine: React.FC<{ dateLabel: string; nowPlaying?: string }> = ({ dateLabel, nowPlaying }) => (
  <div className="flex min-h-[20px] items-center justify-center gap-[7px] text-[15.5px] font-semibold tracking-[-0.2px] text-white/[0.94]" style={{ textShadow: '0 1px 5px rgba(0,0,0,.45)' }}>
    <span className="truncate">{dateLabel}</span>
    {nowPlaying ? (
      <>
        <PlayIcon />
        <span className="max-w-[250px] truncate">{nowPlaying}</span>
      </>
    ) : null}
  </div>
);

const Wallpaper: React.FC<{ url: string }> = ({ url }) => (
  <>
    <img src={url} alt="" aria-hidden="true" className="absolute inset-0 h-full w-full object-cover object-center" />
    <div
      className="pointer-events-none absolute inset-0"
      style={{
        background:
          'linear-gradient(180deg,rgba(0,0,0,.18) 0%,rgba(0,0,0,.04) 38%,rgba(0,0,0,.62) 100%)',
      }}
    />
  </>
);

const LockscreenBody: React.FC<{ config: BaitWidgetConfig; nowPlaying?: string }> = ({ config, nowPlaying }) => (
  <>
    <div className="relative z-10 px-[20px] pt-[44px] text-center">
      <NowLine dateLabel={config.date_label || 'domingo, 2 de noviembre'} nowPlaying={nowPlaying} />
      <h1
        className="mt-[3px] whitespace-nowrap text-[114px] font-bold leading-[0.94] tracking-[-3.6px] text-white/[0.94]"
        style={{ fontFeatureSettings: '"tnum" 1', textShadow: '0 4px 26px rgba(0,0,0,.38)' }}
      >
        {config.timestamp_label || '07:12'}
      </h1>
    </div>
    <IosNotificationStack notifications={config.notifications} />
    <IosBottomActions />
    <IosHomeIndicator className="mb-[6px]" />
  </>
);

export const IosBaitFrame: React.FC<{
  config: BaitWidgetConfig;
  compact?: boolean;
  wallpaperUrl?: string;
  nowPlaying?: string;
}> = ({
  config,
  compact = false,
  wallpaperUrl = '/generated_images/ios17_editorial_dark_wallpaper.png',
  nowPlaying,
}) => {
  const isLockscreen = config.widget_type === 'ios_lockscreen';
  const isNotes = config.widget_type === 'iphone_note_3am';
  const time = config.timestamp_label || '07:12';

  const frame = (
    <div
      className="relative flex flex-col overflow-hidden bg-black text-white select-none"
      style={{ width: FRAME_WIDTH, height: FRAME_HEIGHT, fontFamily: FONT_STACK, lineHeight: 1.2 }}
    >
      {isLockscreen && <Wallpaper url={wallpaperUrl} />}
      <div className="relative z-10 flex h-full flex-col">
        <IosStatusBar label={isLockscreen ? 'TIGO' : time} />
        {isLockscreen && <LockscreenBody config={config} nowPlaying={nowPlaying} />}
        {isNotes && <AppleNotesMode config={config} />}
        {!isLockscreen && !isNotes && <StripeDashboardMode config={config} />}
      </div>
      {isLockscreen && <IosGrain />}
    </div>
  );

  if (!compact) return frame;

  return (
    <div className="relative overflow-hidden" style={{ width: 320, height: 693 }}>
      <div style={{ transform: `scale(${COMPACT_SCALE})`, transformOrigin: 'top left' }}>{frame}</div>
    </div>
  );
};
