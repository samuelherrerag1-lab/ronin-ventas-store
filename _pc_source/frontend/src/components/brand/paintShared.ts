import type { AvatarBackground, BrandCopy } from './brandSpecs';

export interface PaintOptions {
  zoom: number;
  background: AvatarBackground;
  copy: BrandCopy;
}

export const safeName = (copy: BrandCopy): string => copy.name.trim() || 'Tu marca';
export const safeHandle = (copy: BrandCopy): string => copy.handle.trim() || '@tumarca';
