/** Entrada/salida de imágenes: validación, decodificación y descarga. Todo local. */

import { MAX_FILE_BYTES, formatBytes } from './brandSpecs';

/** Devuelve el mensaje de error o null si el archivo es aceptable. */
export function validateImageFile(file: File): string | null {
  if (!file.type || !file.type.startsWith('image/')) {
    return `"${file.name}" no es una imagen. Formatos aceptados: PNG, JPG, WebP, GIF o AVIF.`;
  }
  if (file.size === 0) {
    return `"${file.name}" está vacío (0 bytes).`;
  }
  if (file.size > MAX_FILE_BYTES) {
    return `"${file.name}" pesa ${formatBytes(file.size)} y el límite es 10 MB.`;
  }
  return null;
}

/** Lee el archivo como data URL y espera a que el navegador lo decodifique. */
export function loadImageFromFile(file: File): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(new Error('No se pudo leer el archivo desde el disco.'));
    reader.onload = () => {
      const src = typeof reader.result === 'string' ? reader.result : '';
      if (!src) {
        reject(new Error('El archivo llegó vacío o ilegible.'));
        return;
      }
      const image = new Image();
      image.onload = () => {
        if (image.naturalWidth === 0 || image.naturalHeight === 0) {
          reject(new Error('La imagen no tiene dimensiones válidas.'));
          return;
        }
        resolve(image);
      };
      image.onerror = () => reject(new Error('El navegador no pudo decodificar la imagen. Prueba PNG, JPG o WebP.'));
      image.src = src;
    };
    reader.readAsDataURL(file);
  });
}

/** Fuerza un PNG real desde el canvas. Devuelve false si el navegador no lo permite. */
export function downloadCanvas(canvas: HTMLCanvasElement, filename: string): Promise<boolean> {
  return new Promise((resolve) => {
    canvas.toBlob((blob) => {
      if (!blob) {
        resolve(false);
        return;
      }
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      link.rel = 'noopener';
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 5000);
      resolve(true);
    }, 'image/png');
  });
}
