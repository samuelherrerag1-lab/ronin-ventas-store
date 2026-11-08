import React, { useCallback, useEffect, useRef, useState } from 'react';

/** Observa el ancho real de un contenedor para dibujar SVG con coordenadas en px. */
export function useSize<T extends HTMLElement>(): [React.RefObject<T>, { w: number; h: number }] {
  const ref = useRef<T>(null);
  const [size, setSize] = useState({ w: 0, h: 0 });
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const ro = new ResizeObserver((entries) => {
      const box = entries[0]?.contentRect;
      if (box) setSize({ w: Math.round(box.width), h: Math.round(box.height) });
    });
    ro.observe(el);
    setSize({ w: el.clientWidth, h: el.clientHeight });
    return () => ro.disconnect();
  }, []);
  return [ref, size];
}

/** Contador animado con easing, sin animación si el usuario pide menos movimiento. */
export function useCountUp(target: number, duration = 900): number {
  const [value, setValue] = useState(target);
  const fromRef = useRef(0);
  const rafRef = useRef(0);
  const reduced = typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;

  useEffect(() => {
    if (reduced || !Number.isFinite(target)) {
      setValue(target);
      return;
    }
    const from = fromRef.current;
    const start = performance.now();
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - t, 3);
      setValue(from + (target - from) * eased);
      if (t < 1) rafRef.current = requestAnimationFrame(tick);
      else fromRef.current = target;
    };
    rafRef.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(rafRef.current);
  }, [target, duration, reduced]);

  return value;
}

/** Cierra al hacer click fuera + Escape, para menús y paletas. */
export function useDismiss(onClose: () => void, active: boolean): (node: HTMLElement | null) => void {
  const nodeRef = useRef<HTMLElement | null>(null);
  const setNode = useCallback((node: HTMLElement | null) => {
    nodeRef.current = node;
  }, []);
  useEffect(() => {
    if (!active) return;
    const onDown = (event: MouseEvent) => {
      if (!nodeRef.current) return;
      if (!nodeRef.current.contains(event.target as Node)) onClose();
    };
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose();
    };
    document.addEventListener('mousedown', onDown);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onDown);
      document.removeEventListener('keydown', onKey);
    };
  }, [active, onClose]);
  return setNode;
}

/** Estado persistido (colapso del sidebar, vista del catálogo). */
export function usePersisted<T extends string>(key: string, initial: T): [T, (value: T) => void] {
  const [value, setValue] = useState<T>(() => {
    try {
      const raw = window.localStorage.getItem(`ronin.${key}`);
      return (raw as T) || initial;
    } catch {
      return initial;
    }
  });
  const set = useCallback(
    (next: T) => {
      setValue(next);
      try {
        window.localStorage.setItem(`ronin.${key}`, next);
      } catch {
        /* modo privado: sin persistencia */
      }
    },
    [key],
  );
  return [value, set];
}
