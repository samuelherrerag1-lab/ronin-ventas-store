import React, { useCallback, useEffect, useRef, useState } from 'react';

interface Props {
  label: React.ReactNode;
  children: React.ReactNode;
  side?: 'right' | 'top';
  className?: string;
}

/**
 * Tooltip posicionado en fixed para escapar de paneles con overflow.
 * El primero espera 220 ms; los siguientes son instantáneos (menos fricción).
 */
export const Tip: React.FC<Props> = ({ label, children, side = 'top', className = '' }) => {
  const [open, setOpen] = useState(false);
  const [instant, setInstant] = useState(false);
  const [pos, setPos] = useState({ x: 0, y: 0 });
  const anchor = useRef<HTMLSpanElement | null>(null);
  const timer = useRef(0);

  const place = useCallback(() => {
    const node = anchor.current;
    if (!node) return;
    const rect = node.getBoundingClientRect();
    setPos(
      side === 'right'
        ? { x: rect.right + 10, y: rect.top + rect.height / 2 }
        : { x: rect.left + rect.width / 2, y: rect.top - 8 },
    );
  }, [side]);

  const show = () => {
    window.clearTimeout(timer.current);
    timer.current = window.setTimeout(
      () => {
        place();
        setOpen(true);
        setInstant(true);
      },
      instant ? 0 : 220,
    );
  };

  const hide = () => {
    window.clearTimeout(timer.current);
    setOpen(false);
  };

  useEffect(() => () => window.clearTimeout(timer.current), []);

  return (
    <span
      ref={anchor}
      className={`inline-flex ${className}`}
      onMouseEnter={show}
      onMouseLeave={hide}
      onFocus={show}
      onBlur={hide}
    >
      {children}
      {open && (
        <span
          role="tooltip"
          className="animate-tooltip pointer-events-none fixed z-[80] max-w-[250px] rounded-md border border-line2 bg-[#1b1b21] px-2 py-1 text-[11px] font-normal leading-snug text-ink shadow-[0_10px_30px_rgba(0,0,0,0.6)]"
          style={
            side === 'right'
              ? { left: pos.x, top: pos.y, transform: 'translateY(-50%)' }
              : { left: pos.x, top: pos.y, transform: 'translate(-50%, -100%)' }
          }
        >
          {label}
        </span>
      )}
    </span>
  );
};
