import React from 'react';

export type IconName =
  | 'home' | 'chat' | 'pin' | 'phone' | 'box' | 'upload' | 'shield' | 'chart' | 'brush' | 'plug'
  | 'search' | 'command' | 'refresh' | 'close' | 'copy' | 'check' | 'external' | 'download'
  | 'filter' | 'grid' | 'list' | 'chevron-down' | 'chevron-right' | 'chevron-left' | 'plus'
  | 'play' | 'more' | 'menu' | 'sliders' | 'arrow-right' | 'arrow-up-right' | 'arrow-down-right'
  | 'sort' | 'clock' | 'dollar' | 'route' | 'layers' | 'target' | 'bolt' | 'alert' | 'info'
  | 'wifi' | 'lock' | 'cpu' | 'eye' | 'bell' | 'trash' | 'flame' | 'wrench' | 'cart';

const P: Record<IconName, React.ReactNode> = {
  home: <><path d="M3.5 10.5 12 3.5l8.5 7" /><path d="M5.5 9.2V20h5v-5.5h3V20h5V9.2" /></>,
  chat: <><path d="M20.5 11.5c0 4.1-3.8 7.4-8.5 7.4-1 0-2-.15-2.9-.42L4.5 20l1.1-3.2A7 7 0 0 1 3.5 11.5c0-4.1 3.8-7.4 8.5-7.4s8.5 3.3 8.5 7.4Z" /></>,
  pin: <><path d="M12 21s6.5-6.2 6.5-10.5a6.5 6.5 0 1 0-13 0C5.5 14.8 12 21 12 21Z" /><circle cx="12" cy="10.4" r="2.4" /></>,
  phone: <><rect x="7" y="2.5" width="10" height="19" rx="2.6" /><path d="M10.6 5.4h2.8" /><path d="M10.4 19h3.2" /></>,
  box: <><path d="M20.5 7.6 12 3 3.5 7.6v8.8L12 21l8.5-4.6V7.6Z" /><path d="M3.5 7.6 12 12.2l8.5-4.6M12 12.2V21" /></>,
  upload: <><path d="M12 16V4m0 0 4 4m-4-4-4 4" /><path d="M4 15v3.5A2.5 2.5 0 0 0 6.5 21h11a2.5 2.5 0 0 0 2.5-2.5V15" /></>,
  shield: <><path d="M12 21c5-1.6 8-5.8 8-10.8V6l-8-3-8 3v4.2C4 15.2 7 19.4 12 21Z" /><path d="m8.8 11.8 2.2 2.3 4.2-4.4" /></>,
  chart: <><path d="M3.5 20.5h17" /><path d="M6.5 20V11m5 9V4.5m5 15V8" /></>,
  brush: <><path d="M4 20c2.5.3 3.6-1 4-3l.8-3.2" /><path d="M8.8 13.8 15 7.6a2.8 2.8 0 0 1 4 0l.4.4a2.8 2.8 0 0 1 0 4L13.2 18" /><path d="M16.5 4.5 19.5 7.5" /></>,
  plug: <><path d="M9 3v5m6-5v5" /><path d="M6.5 8h11v3.5a5.5 5.5 0 0 1-11 0V8Z" /><path d="M12 17v4" /></>,
  search: <><circle cx="11" cy="11" r="6.5" /><path d="m16 16 4.5 4.5" /></>,
  command: <><path d="M9 6.5a2.5 2.5 0 1 0-2.5 2.5H9m0-2.5v11m0-11h6m-6 11a2.5 2.5 0 1 1-2.5-2.5H9m6-8.5a2.5 2.5 0 1 1 2.5 2.5H15m0-2.5v11m0 0a2.5 2.5 0 1 0 2.5 2.5H15" /></>,
  refresh: <><path d="M20 12a8 8 0 1 1-2.6-5.9" /><path d="M20 4v4.5h-4.5" /></>,
  close: <><path d="M6 6l12 12M18 6 6 18" /></>,
  copy: <><rect x="8.5" y="8.5" width="12" height="12" rx="2.4" /><path d="M15.5 5.5A2 2 0 0 0 13.5 3.5h-8a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2" /></>,
  check: <><path d="m4.5 12.5 4.6 4.6L19.5 6.8" /></>,
  external: <><path d="M4.5 19.5 19 5m0 0h-9m9 0v9" /></>,
  download: <><path d="M12 3.5v12m0 0 4-4m-4 4-4-4" /><path d="M4.5 17.5v1a2.5 2.5 0 0 0 2.5 2.5h10a2.5 2.5 0 0 0 2.5-2.5v-1" /></>,
  filter: <><path d="M3.5 6h17l-6.6 8v6l-3.8-2v-4L3.5 6Z" /></>,
  grid: <><rect x="3.5" y="3.5" width="7" height="7" rx="1.6" /><rect x="13.5" y="3.5" width="7" height="7" rx="1.6" /><rect x="3.5" y="13.5" width="7" height="7" rx="1.6" /><rect x="13.5" y="13.5" width="7" height="7" rx="1.6" /></>,
  list: <><path d="M4 7h16M4 12h16M4 17h16" /></>,
  'chevron-down': <><path d="m6 9.5 6 6 6-6" /></>,
  'chevron-right': <><path d="m9.5 6 6 6-6 6" /></>,
  'chevron-left': <><path d="m14.5 6-6 6 6 6" /></>,
  plus: <><path d="M12 5v14M5 12h14" /></>,
  play: <><path d="M8 5.5 19 12 8 18.5v-13Z" /></>,
  more: <><circle cx="5.5" cy="12" r="1.4" fill="currentColor" stroke="none" /><circle cx="12" cy="12" r="1.4" fill="currentColor" stroke="none" /><circle cx="18.5" cy="12" r="1.4" fill="currentColor" stroke="none" /></>,
  menu: <><path d="M4 7h16M4 12h16M4 17h16" /></>,
  sliders: <><path d="M4 8h10m4 0h2M4 16h4m4 0h8" /><circle cx="16" cy="8" r="2" /><circle cx="10" cy="16" r="2" /></>,
  'arrow-right': <><path d="M4 12h16m0 0-6-6m6 6-6 6" /></>,
  'arrow-up-right': <><path d="M7 17 17 7m0 0h-7m7 0v7" /></>,
  'arrow-down-right': <><path d="M7 7l10 10m0 0v-7m0 7h-7" /></>,
  sort: <><path d="M8 4.5v15m0 0-3.2-3.2M8 19.5l3.2-3.2M16 19.5v-15m0 0-3.2 3.2M16 4.5l3.2 3.2" /></>,
  clock: <><circle cx="12" cy="12" r="8.5" /><path d="M12 7.5V12l3 2" /></>,
  dollar: <><path d="M12 3v18" /><path d="M16 7.5c0-1.9-1.8-3-4-3s-4 1.1-4 3 1.8 2.8 4 3.3 4 1.4 4 3.4-1.8 3.3-4 3.3-4-1.4-4-3.3" /></>,
  route: <><circle cx="6" cy="6" r="2.4" /><circle cx="18" cy="18" r="2.4" /><path d="M8.4 6H14a4 4 0 0 1 0 8h-4a4 4 0 0 0 0 8h5.6" /></>,
  layers: <><path d="m12 3 8.5 4.5L12 12 3.5 7.5 12 3Z" /><path d="m4 12 8 4.3 8-4.3M4 16.5l8 4.3 8-4.3" /></>,
  target: <><circle cx="12" cy="12" r="8.5" /><circle cx="12" cy="12" r="4.5" /><circle cx="12" cy="12" r="1" fill="currentColor" stroke="none" /></>,
  bolt: <><path d="M13.5 2.5 5 13.5h5.5L9.5 21.5 19 10h-5.5l0-7.5Z" /></>,
  alert: <><path d="M12 3.5 21 20H3L12 3.5Z" /><path d="M12 9.5v4.2" /><circle cx="12" cy="16.6" r=".9" fill="currentColor" stroke="none" /></>,
  info: <><circle cx="12" cy="12" r="8.5" /><path d="M12 11v5.5" /><circle cx="12" cy="8" r=".9" fill="currentColor" stroke="none" /></>,
  wifi: <><path d="M2.5 8.8a14 14 0 0 1 19 0" /><path d="M6 12.3a9 9 0 0 1 12 0" /><path d="M9.3 15.7a4.3 4.3 0 0 1 5.4 0" /><circle cx="12" cy="19" r="1" fill="currentColor" stroke="none" /></>,
  lock: <><rect x="5" y="10.5" width="14" height="10" rx="2.4" /><path d="M8 10.5V8a4 4 0 0 1 8 0v2.5" /></>,
  cpu: <><rect x="6.5" y="6.5" width="11" height="11" rx="2.2" /><path d="M10 3v3.5M14 3v3.5M10 17.5V21m4-3.5V21M3 10h3.5M3 14h3.5M17.5 10H21m-3.5 4H21" /></>,
  eye: <><path d="M2.5 12S6 6 12 6s9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6Z" /><circle cx="12" cy="12" r="2.6" /></>,
  bell: <><path d="M6.5 10a5.5 5.5 0 0 1 11 0c0 4 1.5 5.5 1.5 5.5H5S6.5 14 6.5 10Z" /><path d="M10 18.5a2.2 2.2 0 0 0 4 0" /></>,
  trash: <><path d="M4.5 7h15M9.5 7V4.5h5V7M6.5 7l.8 13h9.4l.8-13" /></>,
  flame: <><path d="M12 21c3.6 0 6-2.3 6-5.4 0-4-3-5.8-4-9.6-2 1.4-3 3.2-3 4.8-1-.6-1.6-1.6-1.8-2.8C7.4 9.4 6 11.6 6 14.8 6 18.4 8.4 21 12 21Z" /></>,
  wrench: <><path d="M20 5.5a5 5 0 0 1-6.6 6.6L6 19.5a2.1 2.1 0 0 1-3-3l7.4-7.4A5 5 0 0 1 17 2.8l-3 3 2.2 2.2 3-3Z" /></>,
  cart: <><path d="M3 4.5h2.5l2.2 10.4h10.6L20.5 7H6.2" /><circle cx="9" cy="19" r="1.4" /><circle cx="17" cy="19" r="1.4" /></>,
};

interface Props {
  name: IconName;
  size?: number;
  className?: string;
  strokeWidth?: number;
}

/** Set único de iconos SVG inline (cero emojis, cero icon-fonts). */
export const Icon: React.FC<Props> = ({ name, size = 16, className = '', strokeWidth = 1.7 }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth={strokeWidth}
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
    aria-hidden="true"
    focusable="false"
  >
    {P[name]}
  </svg>
);
