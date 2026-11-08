import React from 'react';
import { Icon } from '../ui/Icon';
import { Panel, PanelHead, Segmented } from '../ui/primitives';

export interface BaitConfig {
  widgetType: string;
  wallpaperUrl: string;
  headline: string;
  subMetric: string;
  timestamp: string;
  dateLabel: string;
  notifications: string[];
}

interface Props {
  config: BaitConfig;
  wallpapers: { label: string; url: string }[];
  onChange: (patch: Partial<BaitConfig>) => void;
  onNotification: (index: number, value: string) => void;
}

const WIDGETS = [
  { value: 'ios_lockscreen', label: 'Lockscreen' },
  { value: 'stripe_gumroad_dashboard', label: 'Stripe' },
  { value: 'iphone_note_3am', label: 'Notas' },
];

/** Columna de parámetros: controles tipo iOS, etiquetas mínimas. */
export const BaitConfigPanel: React.FC<Props> = ({ config, wallpapers, onChange, onNotification }) => (
  <Panel className="flex flex-col">
    <PanelHead title="Captura" icon="phone" hint="iOS 17.5" />
    <div className="space-y-3 p-3">
      <Segmented
        ariaLabel="Tipo de widget"
        value={config.widgetType}
        onChange={(value) => onChange({ widgetType: value })}
        options={WIDGETS}
        className="w-full justify-between [&>button]:flex-1"
      />

      <div>
        <p className="label mb-1.5">Fondo</p>
        <div className="grid grid-cols-4 gap-1.5">
          {wallpapers.map((wall) => {
            const on = config.wallpaperUrl === wall.url;
            return (
              <button
                key={wall.url}
                type="button"
                onClick={() => onChange({ wallpaperUrl: wall.url })}
                aria-pressed={on}
                aria-label={`Fondo ${wall.label}`}
                title={wall.label}
                className={`overflow-hidden rounded-[5px] border transition-colors duration-150 ${
                  on ? 'border-accent' : 'border-line hover:border-line2'
                }`}
              >
                <img src={wall.url} alt="" className="h-9 w-full object-cover" loading="lazy" />
              </button>
            );
          })}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <label className="block">
          <span className="label">Hora</span>
          <input className="field mt-1 h-8 w-full" value={config.timestamp} onChange={(event) => onChange({ timestamp: event.target.value })} aria-label="Hora de la captura" />
        </label>
        <label className="block">
          <span className="label">Métrica</span>
          <input className="field mt-1 h-8 w-full text-accent" value={config.headline} onChange={(event) => onChange({ headline: event.target.value })} aria-label="Métrica principal" />
        </label>
      </div>

      <label className="block">
        <span className="label">Sub-métrica</span>
        <input className="field mt-1 h-8 w-full" value={config.subMetric} onChange={(event) => onChange({ subMetric: event.target.value })} aria-label="Sub-métrica" />
      </label>

      <label className="block">
        <span className="label">Fecha</span>
        <input className="field mt-1 h-8 w-full" value={config.dateLabel} onChange={(event) => onChange({ dateLabel: event.target.value })} aria-label="Fecha de la captura" />
      </label>

      <div>
        <p className="label mb-1.5 flex items-center justify-between">
          Notificaciones
          <span className="num text-ink3">{config.notifications.length}</span>
        </p>
        <div className="space-y-1.5">
          {config.notifications.map((notification, index) => (
            <div key={index} className="flex items-center gap-1.5">
              <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-[6px] border border-line bg-panel2 text-ink3">
                <Icon name={index === 0 ? 'dollar' : index === 1 ? 'cart' : 'bell'} size={12} />
              </span>
              <input
                className="field h-7 w-full text-[11px]"
                value={notification}
                onChange={(event) => onNotification(index, event.target.value)}
                aria-label={`Notificación ${index + 1}`}
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  </Panel>
);
