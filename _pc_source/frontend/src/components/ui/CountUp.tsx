import React from 'react';
import { useCountUp } from '../../hooks/useUi';
import { num } from '../../utils/format';

interface Props {
  value: number | null | undefined;
  digits?: number;
  prefix?: string;
  suffix?: string;
  className?: string;
  duration?: number;
  /** Si es falso, la cifra se imprime sin animar (histórico, tablas). */
  animate?: boolean;
}

/** Cifra con contador animado; respeta prefers-reduced-motion. */
export const CountUp: React.FC<Props> = ({
  value,
  digits = 0,
  prefix = '',
  suffix = '',
  className = '',
  duration = 900,
  animate = true,
}) => {
  const target = typeof value === 'number' && Number.isFinite(value) ? value : 0;
  const animated = useCountUp(target, duration);
  const shown = animate ? animated : target;
  return (
    <span className={className}>
      {prefix}
      {value === null || value === undefined ? '—' : num(shown, digits)}
      {suffix}
    </span>
  );
};
