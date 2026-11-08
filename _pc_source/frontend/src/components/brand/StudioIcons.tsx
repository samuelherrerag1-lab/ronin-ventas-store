/** Iconografía SVG inline del módulo. Sin emojis, sin librerías. */

import React from 'react';

interface IconProps {
  className?: string;
}

const base = 'w-4 h-4';

const strokeProps = {
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.7,
  strokeLinecap: 'round' as const,
  strokeLinejoin: 'round' as const,
  'aria-hidden': true,
  focusable: 'false' as const,
};

export const UploadIcon: React.FC<IconProps> = ({ className = base }) => (
  <svg viewBox="0 0 24 24" className={className} {...strokeProps}>
    <path d="M12 16V4" />
    <path d="M7.5 8.5 12 4l4.5 4.5" />
    <path d="M4 15v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3" />
  </svg>
);

export const DownloadIcon: React.FC<IconProps> = ({ className = base }) => (
  <svg viewBox="0 0 24 24" className={className} {...strokeProps}>
    <path d="M12 4v12" />
    <path d="M7.5 11.5 12 16l4.5-4.5" />
    <path d="M4 16v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" />
  </svg>
);

export const LockIcon: React.FC<IconProps> = ({ className = base }) => (
  <svg viewBox="0 0 24 24" className={className} {...strokeProps}>
    <rect x="4.5" y="10.5" width="15" height="10" rx="2.5" />
    <path d="M8.5 10.5V7.8a3.5 3.5 0 0 1 7 0v2.7" />
    <path d="M12 15v2" />
  </svg>
);

export const CopyIcon: React.FC<IconProps> = ({ className = base }) => (
  <svg viewBox="0 0 24 24" className={className} {...strokeProps}>
    <rect x="8.5" y="8.5" width="11" height="11" rx="2" />
    <path d="M15.5 8.5V6a2 2 0 0 0-2-2h-7a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h2.5" />
  </svg>
);

export const CheckIcon: React.FC<IconProps> = ({ className = base }) => (
  <svg viewBox="0 0 24 24" className={className} {...strokeProps}>
    <path d="m5 12.5 4.5 4.5L19 7" />
  </svg>
);

export const TrashIcon: React.FC<IconProps> = ({ className = base }) => (
  <svg viewBox="0 0 24 24" className={className} {...strokeProps}>
    <path d="M4 7h16" />
    <path d="M9.5 7V5.5a1.5 1.5 0 0 1 1.5-1.5h2a1.5 1.5 0 0 1 1.5 1.5V7" />
    <path d="M6.5 7 7.6 19a1.6 1.6 0 0 0 1.6 1.5h5.6a1.6 1.6 0 0 0 1.6-1.5L17.5 7" />
    <path d="M10.5 11v5.5M13.5 11v5.5" />
  </svg>
);

export const ImageIcon: React.FC<IconProps> = ({ className = base }) => (
  <svg viewBox="0 0 24 24" className={className} {...strokeProps}>
    <rect x="3.5" y="4.5" width="17" height="15" rx="2.5" />
    <circle cx="9" cy="10" r="1.6" />
    <path d="m4.5 17 4.7-4.7a1.6 1.6 0 0 1 2.3 0l2.2 2.2 1.8-1.8a1.6 1.6 0 0 1 2.3 0l1.7 1.7" />
  </svg>
);

export const SlidersIcon: React.FC<IconProps> = ({ className = base }) => (
  <svg viewBox="0 0 24 24" className={className} {...strokeProps}>
    <path d="M4 8h10M18 8h2M4 16h4M12 16h8" />
    <circle cx="16" cy="8" r="2" />
    <circle cx="10" cy="16" r="2" />
  </svg>
);

export const AlertIcon: React.FC<IconProps> = ({ className = base }) => (
  <svg viewBox="0 0 24 24" className={className} {...strokeProps}>
    <path d="M12 4.5 21 20H3L12 4.5Z" />
    <path d="M12 10v5" />
    <path d="M12 17.8v.2" />
  </svg>
);

export const ArrowUpRightIcon: React.FC<IconProps> = ({ className = base }) => (
  <svg viewBox="0 0 24 24" className={className} {...strokeProps}>
    <path d="M7 17 17 7" />
    <path d="M8.5 7H17v8.5" />
  </svg>
);
