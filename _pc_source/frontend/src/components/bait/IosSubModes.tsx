import React from 'react';
import type { BaitWidgetConfig } from '../../types/domain';
import { IosHomeIndicator } from './IosBaitChrome';

/**
 * Modos de app (Apple Notes 3:14 AM y Stripe Express).
 * Comparten la barra de estado v2 que dibuja IosBaitFrame: aqui solo
 * vive la barra de navegacion propia de cada app.
 */

export const AppleNotesMode: React.FC<{ config: BaitWidgetConfig }> = ({ config }) => {
  const checks = (config.notifications?.length
    ? config.notifications
    : [
        'Estrategia silenciosa probada a las 3:14 AM',
        '91% de margen neto sin intermediarios',
        'Checkout optimizado con order bump +$9',
      ]
  ).slice(0, 3);

  return (
    <div className="flex h-full flex-col justify-between bg-black">
      <div>
        <div className="flex items-center justify-between pl-[16px] pr-[20px] pb-[8px] pt-[4px] text-[#FFD60A]">
          <div className="flex items-center gap-[3px]">
            <svg aria-hidden="true" className="h-5 w-5 fill-none stroke-[#FFD60A]" strokeWidth="2.5" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
            <span className="text-[17px] font-medium">Carpetas</span>
          </div>
          <div className="flex items-center gap-[18px]">
            <svg aria-hidden="true" className="h-[19px] w-[19px] fill-none stroke-[#FFD60A]" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8m-4-6l-4-4-4 4m4-4v13" />
            </svg>
            <div className="flex h-[22px] w-[22px] items-center justify-center rounded-full border-[1.6px] border-[#FFD60A]">
              <svg aria-hidden="true" className="h-[4px] w-[12px] fill-[#FFD60A]" viewBox="0 0 12 4">
                <circle cx="2" cy="2" r="1.5" />
                <circle cx="6" cy="2" r="1.5" />
                <circle cx="10" cy="2" r="1.5" />
              </svg>
            </div>
            <span className="text-[17px] font-semibold">Listo</span>
          </div>
        </div>

        <div className="px-[24px]">
          <p className="mb-[16px] mt-[6px] text-center text-[12px] font-medium text-[#8E8E93]">
            {config.date_label || '2 de noviembre de 2026'} a las {config.timestamp_label || '03:14'} a. m.
          </p>

          <h2 className="mb-[12px] text-[24px] font-bold leading-[1.28] tracking-[-0.4px] text-white">
            {config.headline_metric}
          </h2>

          <p className="mb-[14px] text-[14.5px] leading-[1.48] text-[#E5E5E7]">
            Nadie compra otro curso de 40 horas.{' '}
            <span className="rounded-[4px] bg-[#FFD60A]/18 px-1.5 py-0.5 font-semibold text-[#FFE66D]">
              La gente paga por velocidad, asimetría y atajos listos
            </span>{' '}
            que resuelven un dolor sangrante en 5 minutos:
          </p>

          <div className="mb-[16px] text-[13.5px] leading-[1.4] text-[#D1D1D6]">
            <p>• 1 micro-asset digital de 1 sola página genera más flujo que una agencia entera.</p>
            <p>• Cero inventario, cero llamadas, cero clientes fastidiosos.</p>
            <p>• Tráfico de curiosidad oscura con entrega 100% instantánea.</p>
          </div>

          <div>
            {checks.map((item, i) => (
              <div key={i} className="mb-[11px] flex items-start gap-[11px] text-[14px] text-[#F2F2F7]">
                <div className="mt-px flex h-[19px] w-[19px] shrink-0 items-center justify-center rounded-full bg-[#FFD60A]">
                  <svg aria-hidden="true" className="h-3 w-3 fill-none stroke-black" strokeWidth="3.5" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M20 6 9 17l-5-5" />
                  </svg>
                </div>
                <div className="leading-[1.4]">{item.replace(/^(Gumroad|Hotmart|Stripe)\s*[•:\-]?\s*/i, '')}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="shrink-0 border-t-[0.5px] border-white/12 px-[24px] pb-[22px] pt-[10px]">
        <div className="flex items-center justify-between pb-[6px] text-[#FFD60A]">
          <svg aria-hidden="true" className="h-[22px] w-[22px] fill-none stroke-current" strokeWidth="2" viewBox="0 0 24 24">
            <rect x="3" y="3" width="18" height="18" rx="2" />
            <path d="M3 9h18M9 21V9" />
          </svg>
          <svg aria-hidden="true" className="h-[22px] w-[22px] fill-none stroke-current" strokeWidth="2" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" />
            <path d="m9 12 2 2 4-4" />
          </svg>
          <svg aria-hidden="true" className="h-[22px] w-[22px] fill-none stroke-current" strokeWidth="2" viewBox="0 0 24 24">
            <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z" />
            <circle cx="12" cy="13" r="3" />
          </svg>
          <svg aria-hidden="true" className="h-[22px] w-[22px] fill-none stroke-current" strokeWidth="2" viewBox="0 0 24 24">
            <path d="M12 20h9" />
            <path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z" />
          </svg>
          <svg aria-hidden="true" className="h-[22px] w-[22px] fill-none stroke-current" strokeWidth="2" viewBox="0 0 24 24">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
            <path d="M18.5 2.5a2.12 2.12 0 0 1 3 3L12 15l-4 1 1-4Z" />
          </svg>
        </div>
        <IosHomeIndicator className="mt-[12px]" />
      </div>
    </div>
  );
};

export const StripeDashboardMode: React.FC<{ config: BaitWidgetConfig }> = ({ config }) => {
  const methods = ['Apple Pay •••• 8814', 'Nequi PSE Instant', 'Visa •••• 4242'];
  const times = ['03:12', '02:58', '02:41'];
  const activity = config.notifications?.length
    ? config.notifications
    : ['Bóveda 500 Hooks: $27.00 USD', 'Kit Sistema Completo: $47.00 USD', 'Order Bump Máquina: $19.00 USD'];

  return (
    <div className="flex h-full flex-col justify-between bg-[#0A0D14]">
      <div>
        <div className="flex items-center justify-between border-b-[0.5px] border-white/8 pl-[20px] pr-[20px] pb-[10px] pt-[2px]">
          <div className="flex items-center gap-[8px]">
            <div className="flex h-[22px] w-[22px] items-center justify-center rounded-[6px] bg-[#635BFF] text-[12px] font-black text-white">
              S
            </div>
            <span className="flex items-center gap-1 text-[14px] font-semibold tracking-[-0.2px] text-white">
              ronoverthinks • Express
              <svg className="h-[9px] w-[9px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.4} aria-hidden="true"><path d="m6 9 6 6 6-6" strokeLinecap="round" strokeLinejoin="round" /></svg>
            </span>
          </div>
          <div className="flex gap-[4px] rounded-[8px] border-[0.5px] border-white/8 bg-[#131722] p-[3px] text-[10.5px] font-semibold">
            <span className="rounded-[5px] bg-[#635BFF] px-[8px] py-[2px] text-white">Hoy</span>
            <span className="px-[8px] py-[2px] text-[#8E95A5]">7D</span>
            <span className="px-[8px] py-[2px] text-[#8E95A5]">30D</span>
          </div>
        </div>

        <div className="px-[20px] pt-[16px]">
          <div className="rounded-[18px] border-[0.5px] border-white/8 bg-[#12151E] p-[16px] shadow-[0_8px_24px_rgba(0,0,0,0.4)]">
            <div className="flex items-center justify-between">
              <span className="text-[10.5px] font-bold uppercase tracking-[0.8px] text-[#8E95A5]">Volumen Bruto Hoy</span>
              <span className="rounded-full border-[0.5px] border-[#10B981]/30 bg-[#10B981]/15 px-[7px] py-[2px] text-[11px] font-bold text-[#10B981]">
                +342.8%
              </span>
            </div>
            <div
              className="my-[2px] text-[34px] font-extrabold leading-tight tracking-[-0.8px] text-white"
              style={{ fontFeatureSettings: '"tnum" 1' }}
            >
              {config.headline_metric}
            </div>
            <div className="text-[12px] text-[#8E95A5]">{config.sub_metric}</div>

            <div className="my-[12px] h-[90px] w-full">
              <svg className="h-full w-full overflow-visible" viewBox="0 0 300 75" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="stGradReact" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#10B981" stopOpacity="0.38" />
                    <stop offset="100%" stopColor="#10B981" stopOpacity="0" />
                  </linearGradient>
                </defs>
                <path d="M0,66 Q45,60 80,49 T155,34 T225,18 T285,8 L296,5 L296,75 L0,75 Z" fill="url(#stGradReact)" />
                <path d="M0,66 Q45,60 80,49 T155,34 T225,18 T285,8 L296,5" fill="none" stroke="#10B981" strokeWidth="2.5" strokeLinecap="round" />
                <circle cx="296" cy="5" r="4" fill="#10B981" />
              </svg>
            </div>
            <div className="flex justify-between border-t-[0.5px] border-white/6 pt-[4px] font-mono text-[10px] text-[#6B7280]">
              <span>00:00</span>
              <span>06:00</span>
              <span>12:00</span>
              <span>18:00</span>
              <span className="font-bold text-[#10B981]">Ahora</span>
            </div>
          </div>

          <div className="mt-[12px] grid grid-cols-2 gap-[10px]">
            <div className="rounded-[14px] border-[0.5px] border-white/6 bg-[#12151E] p-[12px]">
              <div className="text-[10px] font-bold uppercase text-[#8E95A5]">Conversión</div>
              <div className="mt-[3px] text-[16px] font-extrabold text-white">4.82%</div>
            </div>
            <div className="rounded-[14px] border-[0.5px] border-white/6 bg-[#12151E] p-[12px]">
              <div className="text-[10px] font-bold uppercase text-[#8E95A5]">Ticket Medio</div>
              <div className="mt-[3px] text-[16px] font-extrabold text-[#F59E0B]">$24.50 USD</div>
            </div>
          </div>

          <div className="mt-[14px]">
            <div className="mb-[8px] text-[10.5px] font-bold uppercase tracking-[0.8px] text-[#8E95A5]">
              Actividad en Tiempo Real
            </div>
            {activity.slice(0, 3).map((item, i) => (
              <div
                key={i}
                className="mb-[7px] flex items-center justify-between rounded-[12px] border-[0.5px] border-white/6 bg-[#12151E] px-[12px] py-[9px]"
              >
                <div className="min-w-0 pr-2">
                  <div className="truncate text-[12.5px] font-semibold text-white">
                    {item.replace(/^(Gumroad|Hotmart|Stripe)\s*[•:\-]?\s*/i, '')}
                  </div>
                  <div className="mt-[2px] font-mono text-[10.5px] text-[#8E95A5]">
                    {methods[i % methods.length]} • {times[i % times.length]}
                  </div>
                </div>
                <span className="shrink-0 rounded-[5px] border-[0.5px] border-[#10B981]/30 bg-[#10B981]/15 px-[7px] py-[2px] text-[10px] font-bold text-[#10B981]">
                  Pagado
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <IosHomeIndicator className="mb-[12px]" />
    </div>
  );
};
