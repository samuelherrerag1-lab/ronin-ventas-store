import React from 'react';
import { Icon, type IconName } from './Icon';
import { signed } from '../../utils/format';

/* ---------- Panel ---------- */
export const Panel: React.FC<{
  children: React.ReactNode;
  className?: string;
  as?: 'section' | 'div' | 'article';
  label?: string;
}> = ({ children, className = '', as: Tag = 'section', label }) => (
  <Tag className={`panel ${className}`} aria-label={label}>
    {children}
  </Tag>
);

export const PanelHead: React.FC<{
  title: string;
  icon?: IconName;
  hint?: string;
  actions?: React.ReactNode;
  className?: string;
}> = ({ title, icon, hint, actions, className = '' }) => (
  <header className={`panel-head ${className}`}>
    <div className="flex min-w-0 items-center gap-2">
      {icon && <Icon name={icon} size={14} className="shrink-0 text-ink3" />}
      <h2 className="truncate text-[12.5px] font-medium text-ink">{title}</h2>
      {hint && <span className="hidden truncate text-[11px] text-ink3 sm:inline">· {hint}</span>}
    </div>
    {actions && <div className="flex shrink-0 items-center gap-1.5">{actions}</div>}
  </header>
);

/* ---------- Estado ---------- */
export const StatusDot: React.FC<{ tone: 'pos' | 'neg' | 'warn' | 'mute'; label: string }> = ({
  tone,
  label,
}) => {
  const color = tone === 'pos' ? 'var(--pos)' : tone === 'neg' ? 'var(--neg)' : tone === 'warn' ? 'var(--warn)' : 'var(--ink-3)';
  return (
    <span className="inline-flex items-center gap-1.5">
      <span className="dot" style={{ background: color }} aria-hidden="true" />
      <span className="sr-only">{label}</span>
    </span>
  );
};

/* ---------- Delta ---------- */
interface DeltaProps {
  value: number | null;
  /** Dirección buena de la métrica: el color dice bueno/malo, no sube/baja. */
  good?: boolean;
  window?: string;
  digits?: number;
  suffix?: string;
}

export const Delta: React.FC<DeltaProps> = ({ value, good, window, digits = 1, suffix = '%' }) => {
  if (value === null || !Number.isFinite(value)) {
    return (
      <span className="text-[11px] text-ink3" title="Sin periodo anterior con el que comparar">
        —
      </span>
    );
  }
  const tone = Math.abs(value) < 0.05 ? 'var(--ink-3)' : good ? 'var(--pos)' : 'var(--neg)';
  return (
    <span className="inline-flex items-baseline gap-1 text-[11px]">
      <span className="num font-medium" style={{ color: tone }}>
        {signed(value, digits, suffix)}
      </span>
      {window && <span className="text-ink3">{window}</span>}
    </span>
  );
};

/* ---------- Vacío honesto ---------- */
export const Empty: React.FC<{
  icon: IconName;
  title: string;
  text: string;
  action?: React.ReactNode;
  compact?: boolean;
}> = ({ icon, title, text, action, compact }) => (
  <div
    className={`flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-line text-center ${
      compact ? 'px-4 py-5' : 'px-6 py-9'
    }`}
  >
    <span className="flex h-8 w-8 items-center justify-center rounded-full border border-line bg-panel2 text-ink3">
      <Icon name={icon} size={15} />
    </span>
    <p className="text-[13px] font-medium text-ink">{title}</p>
    <p className="max-w-[42ch] text-[11.5px] leading-relaxed text-ink3">{text}</p>
    {action && <div className="mt-1 flex flex-wrap items-center justify-center gap-2">{action}</div>}
  </div>
);

/* ---------- Skeleton ---------- */
export const SkeletonRows: React.FC<{ rows?: number; height?: number; className?: string }> = ({
  rows = 4,
  height = 44,
  className = '',
}) => (
  <div className={`space-y-1.5 ${className}`} aria-hidden="true">
    {Array.from({ length: rows }).map((_, i) => (
      <div key={i} className="skel" style={{ height, opacity: 1 - i * 0.12 }} />
    ))}
  </div>
);

/* ---------- Segmentado ---------- */
export const Segmented = <T extends string>({
  value,
  options,
  onChange,
  ariaLabel,
  className = '',
}: {
  value: T;
  options: { value: T; label: string }[];
  onChange: (value: T) => void;
  ariaLabel: string;
  className?: string;
}) => (
  <div className={`seg no-scrollbar max-w-full overflow-x-auto ${className}`} role="group" aria-label={ariaLabel}>
    {options.map((opt) => (
      <button
        key={opt.value}
        type="button"
        aria-pressed={value === opt.value}
        onClick={() => onChange(opt.value)}
      >
        {opt.label}
      </button>
    ))}
  </div>
);

/* ---------- Etiqueta de cifra ---------- */
export const Unit: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <span className="unit">{children}</span>
);
