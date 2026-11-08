import React from 'react';

interface Props {
  values: number[];
  height?: number;
  /** 'accent' marca la serie principal del producto; 'ink' para series de apoyo. */
  tone?: 'accent' | 'ink' | 'muted';
  area?: boolean;
  className?: string;
  title?: string;
}

const COLORS = {
  accent: 'var(--accent)',
  ink: 'var(--ink-2)',
  muted: 'var(--ink-3)',
} as const;

/**
 * Sparkline dibujada a mano (sin librerías): viewBox normalizado 0..100 y trazo
 * con vector-effect para que el grosor no se deforme al estirar.
 * Una serie sin registros se dibuja como línea base discontinua, no como una raya.
 */
export const Sparkline: React.FC<Props> = ({
  values,
  height = 28,
  tone = 'accent',
  area = true,
  className = '',
  title,
}) => {
  const color = COLORS[tone];
  const points = values.length > 1 ? values : [0, 0];
  const min = Math.min(...points);
  const max = Math.max(...points);
  const flat = max === min;
  const span = max - min || 1;
  const step = 100 / (points.length - 1);
  const coords = points.map((value, i) => {
    const x = i * step;
    const y = flat ? 22 : 30 - ((value - min) / span) * 26 - 2;
    return `${x.toFixed(2)},${y.toFixed(2)}`;
  });
  const line = `M${coords.join(' L')}`;
  const fill = `${line} L100,32 L0,32 Z`;

  return (
    <svg
      viewBox="0 0 100 32"
      preserveAspectRatio="none"
      height={height}
      className={`w-full overflow-hidden ${className}`}
      role={title ? 'img' : 'presentation'}
      aria-label={title}
      aria-hidden={title ? undefined : true}
    >
      {flat ? (
        <line
          x1="0"
          x2="100"
          y1="22"
          y2="22"
          stroke="var(--line-2)"
          strokeWidth="1"
          strokeDasharray="3 4"
          vectorEffect="non-scaling-stroke"
        />
      ) : (
        <>
          {area && <path d={fill} fill={color} opacity={tone === 'accent' ? 0.1 : 0.06} />}
          <path
            d={line}
            fill="none"
            stroke={color}
            strokeWidth={1.5}
            strokeLinecap="round"
            strokeLinejoin="round"
            vectorEffect="non-scaling-stroke"
            opacity={tone === 'muted' ? 0.85 : 1}
          />
          <circle cx={100} cy={Number(coords[coords.length - 1].split(',')[1])} r={1.7} fill={color} />
        </>
      )}
    </svg>
  );
};
