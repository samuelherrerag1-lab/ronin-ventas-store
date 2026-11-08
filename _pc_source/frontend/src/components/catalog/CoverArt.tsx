import React, { useState } from 'react';

interface CoverArtProps {
  skuId: string;
  title: string;
  variant?: string;
  className?: string;
}

export const CoverArt: React.FC<CoverArtProps> = ({ skuId, title, variant = 'v1', className = '' }) => {
  const [error, setError] = useState(false);
  const primarySrc = `/product_art/covers/${skuId}_${variant}.webp`;
  const fallbackSrc = `/product_art/${skuId}.webp`;

  if (error) {
    return (
      <div className={`aspect-[3/4] bg-gradient-to-b from-zinc-900 to-black rounded-lg border border-white/10 flex flex-col items-center justify-center p-3 text-center ${className}`}>
        <span className="text-[10px] font-mono-tech text-amber-400 font-bold tracking-wider">{skuId}</span>
        <span className="text-[9px] text-zinc-500 mt-1 line-clamp-2">{title}</span>
      </div>
    );
  }

  return (
    <div className={`relative aspect-[3/4] rounded-lg overflow-hidden border border-white/10 bg-black/80 shadow-md group ${className}`}>
      <img
        src={primarySrc}
        alt={`${title} Cover`}
        loading="lazy"
        onError={(e) => {
          if (e.currentTarget.src.includes(`_${variant}.webp`)) {
            e.currentTarget.src = fallbackSrc;
          } else {
            setError(true);
          }
        }}
        className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
      />
      <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-2 pointer-events-none">
        <span className="text-[9px] font-mono-tech text-amber-300 font-bold">{skuId}</span>
      </div>
    </div>
  );
};
