import React from 'react';

interface Props {
  size?: number;
  className?: string;
  title?: string;
}

/**
 * Marca de Ronin: la pantalla bloqueada (rect redondeado) atravesada por la línea
 * de corte del criterio de 14 días. Un solo trazo de acento.
 */
export const BrandMark: React.FC<Props> = ({ size = 26, className = '', title }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 32 32"
    fill="none"
    className={className}
    role={title ? 'img' : 'presentation'}
    aria-label={title}
    aria-hidden={title ? undefined : true}
  >
    <rect x="7.5" y="3.5" width="17" height="25" rx="4.5" stroke="currentColor" strokeWidth="1.6" />
    <path d="M12 6.6h8" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" opacity="0.55" />
    <path d="M11 11.5h10M11 15h6.5M11 18.5h8" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" opacity="0.4" />
    <path d="M4.5 27.5 27.5 4.5" stroke="var(--accent)" strokeWidth="2.4" strokeLinecap="round" />
  </svg>
);
