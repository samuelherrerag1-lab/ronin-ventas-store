import html as html_lib
import re
from typing import List
from backend.services.ios_html_templates import CSP_META, STATUS_BAR_APP, get_font_css


def build_ios17_notes_html(
    headline_metric: str,
    sub_metric: str,
    notifications: List[str],
    timestamp_label: str = "03:14",
    date_label: str = "2 de noviembre de 2026",
) -> str:
    checks = notifications if notifications else [
        "Estrategia silenciosa probada a las 3:14 AM",
        "91% de margen neto sin intermediarios",
        "Checkout optimizado con order bump +$9 USD",
    ]
    cleaned_checks = [re.sub(r"^(Gumroad|Hotmart|Stripe)\s*[•:\-]?\s*", "", c, flags=re.IGNORECASE) for c in checks]
    checks_html = "".join(
        f"""
        <div class="note-check-item">
          <div class="check-circ">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
          </div>
          <div class="check-text">{html_lib.escape(c)}</div>
        </div>
        """
        for c in cleaned_checks[:4]
    )
    font_css = get_font_css()
    safe_headline = html_lib.escape(headline_metric or "")
    safe_sub = html_lib.escape(sub_metric or "")
    safe_date = html_lib.escape(date_label or "")
    safe_time = html_lib.escape(timestamp_label or "")

    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">{CSP_META}<style>
    {font_css}
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: "SF Pro Display", -apple-system, BlinkMacSystemFont, "Inter", sans-serif; -webkit-font-smoothing: antialiased; }}
    body {{ width: 393px; height: 852px; overflow: hidden; background: #000; color: #fff; position: relative; display: flex; flex-direction: column; justify-content: space-between; }}
    .status-bar {{ height: 54px; padding: 14px 30px 0 30px; display: flex; justify-content: space-between; align-items: center; }}
    .carrier-text {{ font-size: 15px; font-weight: 600; letter-spacing: -0.2px; }}
    .status-cluster {{ display: flex; align-items: center; gap: 6px; }}
    .cell-icon {{ width: 17px; height: 11px; }}
    .net-text {{ font-size: 12px; font-weight: 700; }}
    .battery-wrap {{ display: flex; align-items: center; }}
    .battery-shell {{ width: 24px; height: 12px; border: 1px solid rgba(255,255,255,0.45); border-radius: 3.8px; padding: 1.5px; }}
    .battery-fill {{ width: 100%; height: 100%; background: #fff; border-radius: 1.5px; }}
    .battery-cap {{ width: 1.5px; height: 4.5px; background: rgba(255,255,255,0.45); border-radius: 0 1px 1px 0; }}
    .notes-nav {{ display: flex; justify-content: space-between; align-items: center; padding: 4px 20px 8px 16px; color: #FFD60A; }}
    .back-btn {{ display: flex; align-items: center; font-size: 17px; font-weight: 500; gap: 3px; cursor: pointer; }}
    .nav-actions {{ display: flex; align-items: center; gap: 18px; }}
    .more-circle {{ width: 22px; height: 22px; border-radius: 50%; border: 1.6px solid #FFD60A; display: flex; align-items: center; justify-content: center; }}
    .done-btn {{ font-size: 17px; font-weight: 600; }}
    .content-area {{ padding: 0 24px; flex: 1; }}
    .date-line {{ font-size: 12px; color: #8E8E93; text-align: center; margin: 6px 0 16px; font-weight: 500; }}
    .note-h1 {{ font-size: 24px; font-weight: 700; line-height: 1.28; letter-spacing: -0.4px; color: #fff; margin-bottom: 12px; }}
    .note-p {{ font-size: 14.5px; line-height: 1.48; color: #E5E5E7; margin-bottom: 14px; }}
    .highlight-badge {{ background: rgba(255, 214, 10, 0.18); color: #FFE66D; padding: 2px 6px; border-radius: 4px; font-weight: 600; }}
    .raw-bullets {{ font-size: 13.5px; color: #D1D1D6; line-height: 1.4; margin-bottom: 16px; }}
    .note-check-item {{ display: flex; align-items: flex-start; gap: 11px; margin-bottom: 11px; font-size: 14px; color: #F2F2F7; }}
    .check-circ {{ width: 19px; height: 19px; border-radius: 50%; background: #FFD60A; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 1px; }}
    .notes-toolbar {{ border-top: 0.5px solid rgba(255,255,255,0.12); padding: 10px 24px 22px; position: relative; }}
    .tools-row {{ display: flex; justify-content: space-between; align-items: center; color: #FFD60A; padding-bottom: 6px; }}
    .home-indicator {{ width: 134px; height: 5px; background: rgba(255,255,255,0.95); border-radius: 100px; margin: 12px auto 0; }}
    </style></head><body>
    <div>
      {STATUS_BAR_APP}
      <div class="notes-nav">
        <div class="back-btn">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FFD60A" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>
          <span>Carpetas</span>
        </div>
        <div class="nav-actions">
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="#FFD60A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path><polyline points="16 6 12 2 8 6"></polyline><line x1="12" y1="2" x2="12" y2="15"></line></svg>
          <div class="more-circle"><svg width="12" height="4" viewBox="0 0 12 4" fill="#FFD60A"><circle cx="2" cy="2" r="1.5"/><circle cx="6" cy="2" r="1.5"/><circle cx="10" cy="2" r="1.5"/></svg></div>
          <span class="done-btn">Listo</span>
        </div>
      </div>
      <div class="content-area">
        <div class="date-line">{safe_date} a las {safe_time} a. m.</div>
        <h1 class="note-h1">{safe_headline}</h1>
        <p class="note-p">Nadie compra otro curso de 40 horas. <span class="highlight-badge">La gente paga por velocidad, asimetría y atajos listos</span> que resuelven un dolor sangrante en 5 minutos:</p>
        <div class="raw-bullets">
          <p>• 1 micro-asset digital de 1 sola página genera más flujo que una agencia entera.</p>
          <p>• Cero inventario, cero llamadas, cero clientes fastidiosos.</p>
          <p>• Tráfico de curiosidad oscura con entrega 100% instantánea.</p>
        </div>
        <div class="check-list">{checks_html}</div>
      </div>
    </div>
    <div class="notes-toolbar">
      <div class="tools-row">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/></svg>
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/></svg>
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.12 2.12 0 0 1 3 3L12 15l-4 1 1-4Z"/></svg>
      </div>
      <div class="home-indicator"></div>
    </div>
    </body></html>"""


def build_ios17_stripe_html(
    headline_metric: str,
    sub_metric: str,
    notifications: List[str],
    timestamp_label: str = "03:14",
) -> str:
    txs = notifications if notifications else [
        "Bóveda 500 Hooks: $27.00 USD",
        "Kit Sistema Completo: $47.00 USD",
        "Order Bump Maquina: $19.00 USD",
    ]
    methods = ["Apple Pay •••• 8814", "Nequi PSE Instant", "Visa •••• 4242"]
    times = ["03:12", "02:58", "02:41"]
    tx_html = "".join(
        f"""
        <div class="tx-item">
          <div>
            <div class="tx-title">{html_lib.escape(re.sub(r"^(Gumroad|Hotmart|Stripe)\s*[•:\-]?\s*", "", t, flags=re.IGNORECASE))}</div>
            <div class="tx-sub">{methods[i % 3]} • {times[i % 3]}</div>
          </div>
          <span class="tx-badge">Pagado</span>
        </div>
        """
        for i, t in enumerate(txs[:3])
    )
    font_css = get_font_css()
    safe_headline = html_lib.escape(headline_metric or "")
    safe_sub = html_lib.escape(sub_metric or "")

    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">{CSP_META}<style>
    {font_css}
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: "SF Pro Display", -apple-system, BlinkMacSystemFont, "Inter", sans-serif; -webkit-font-smoothing: antialiased; }}
    body {{ width: 393px; height: 852px; overflow: hidden; background: #0A0D14; color: #fff; position: relative; display: flex; flex-direction: column; justify-content: space-between; }}
    .status-bar {{ height: 54px; padding: 14px 30px 0 30px; display: flex; justify-content: space-between; align-items: center; }}
    .carrier-text {{ font-size: 15px; font-weight: 600; letter-spacing: -0.2px; }}
    .status-cluster {{ display: flex; align-items: center; gap: 6px; }}
    .cell-icon {{ width: 17px; height: 11px; }}
    .net-text {{ font-size: 12px; font-weight: 700; }}
    .battery-wrap {{ display: flex; align-items: center; }}
    .battery-shell {{ width: 24px; height: 12px; border: 1px solid rgba(255,255,255,0.45); border-radius: 3.8px; padding: 1.5px; }}
    .battery-fill {{ width: 100%; height: 100%; background: #fff; border-radius: 1.5px; }}
    .battery-cap {{ width: 1.5px; height: 4.5px; background: rgba(255,255,255,0.45); border-radius: 0 1px 1px 0; }}
    .stripe-nav {{ display: flex; justify-content: space-between; align-items: center; padding: 2px 20px 10px; border-bottom: 0.5px solid rgba(255,255,255,0.08); }}
    .acc-wrap {{ display: flex; align-items: center; gap: 8px; }}
    .stripe-sq {{ width: 22px; height: 22px; border-radius: 6px; background: #635BFF; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 900; }}
    .acc-name {{ font-size: 14px; font-weight: 600; letter-spacing: -0.2px; }}
    .pill-tabs {{ display: flex; gap: 4px; background: #131722; padding: 3px; border-radius: 8px; border: 0.5px solid rgba(255,255,255,0.08); font-size: 10.5px; font-weight: 600; }}
    .pill-act {{ background: #635BFF; padding: 2px 8px; border-radius: 5px; color: #fff; }}
    .pill-inact {{ padding: 2px 8px; color: #8E95A5; }}
    .main-body {{ padding: 16px 20px; flex: 1; }}
    .chart-card {{ background: #12151E; border: 0.5px solid rgba(255,255,255,0.08); border-radius: 18px; padding: 16px; box-shadow: 0 8px 24px rgba(0,0,0,0.4); }}
    .chart-top {{ display: flex; justify-content: space-between; align-items: center; }}
    .chart-lbl {{ font-size: 10.5px; text-transform: uppercase; letter-spacing: 0.8px; color: #8E95A5; font-weight: 700; }}
    .badge-growth {{ font-size: 11px; font-weight: 700; color: #10B981; background: rgba(16,185,129,0.15); border: 0.5px solid rgba(16,185,129,0.3); padding: 2px 7px; border-radius: 99px; }}
    .metric-val {{ font-size: 34px; font-weight: 800; letter-spacing: -0.8px; margin: 4px 0 2px; font-feature-settings: "tnum"; }}
    .metric-sub {{ font-size: 12px; color: #8E95A5; }}
    .chart-svg-box {{ height: 90px; width: 100%; margin: 12px 0 6px; }}
    .chart-axis {{ display: flex; justify-content: space-between; font-size: 10px; color: #6B7280; font-family: monospace; border-top: 0.5px solid rgba(255,255,255,0.06); padding-top: 4px; }}
    .kpi-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 12px; }}
    .kpi-card {{ background: #12151E; border: 0.5px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 12px; }}
    .kpi-t {{ font-size: 10px; text-transform: uppercase; color: #8E95A5; font-weight: 700; }}
    .kpi-v {{ font-size: 16px; font-weight: 800; color: #fff; margin-top: 3px; }}
    .tx-sect {{ margin-top: 14px; }}
    .tx-hdr {{ font-size: 10.5px; text-transform: uppercase; letter-spacing: 0.8px; color: #8E95A5; font-weight: 700; margin-bottom: 8px; }}
    .tx-item {{ display: flex; justify-content: space-between; align-items: center; background: #12151E; border: 0.5px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 9px 12px; margin-bottom: 7px; }}
    .tx-title {{ font-size: 12.5px; font-weight: 600; color: #fff; }}
    .tx-sub {{ font-size: 10.5px; color: #8E95A5; margin-top: 2px; font-family: monospace; }}
    .tx-badge {{ font-size: 10px; font-weight: 700; color: #10B981; background: rgba(16,185,129,0.15); border: 0.5px solid rgba(16,185,129,0.3); padding: 2px 7px; border-radius: 5px; }}
    .home-indicator {{ width: 134px; height: 5px; background: rgba(255,255,255,0.95); border-radius: 100px; margin: 0 auto 12px; }}
    </style></head><body>
    <div>
      {STATUS_BAR_APP}
      <div class="stripe-nav">
        <div class="acc-wrap"><div class="stripe-sq">S</div><span class="acc-name">ronoverthinks • Express ▾</span></div>
        <div class="pill-tabs"><span class="pill-act">Hoy</span><span class="pill-inact">7D</span><span class="pill-inact">30D</span></div>
      </div>
      <div class="main-body">
        <div class="chart-card">
          <div class="chart-top"><span class="chart-lbl">Volumen Bruto Hoy</span><span class="badge-growth">+342.8%</span></div>
          <div class="metric-val">{safe_headline}</div>
          <div class="metric-sub">{safe_sub}</div>
          <div class="chart-svg-box">
            <svg viewBox="0 0 300 75" style="width:100%;height:100%;overflow:visible;">
              <defs><linearGradient id="stGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#10B981" stop-opacity="0.38"/><stop offset="100%" stop-color="#10B981" stop-opacity="0"/></linearGradient></defs>
              <path d="M0,66 Q45,60 80,49 T155,34 T225,18 T285,8 L296,5 L296,75 L0,75 Z" fill="url(#stGrad)"/>
              <path d="M0,66 Q45,60 80,49 T155,34 T225,18 T285,8 L296,5" fill="none" stroke="#10B981" stroke-width="2.5" stroke-linecap="round"/>
              <circle cx="296" cy="5" r="4" fill="#10B981"/>
            </svg>
          </div>
          <div class="chart-axis"><span>00:00</span><span>06:00</span><span>12:00</span><span>18:00</span><span style="color:#10B981;">Ahora</span></div>
        </div>
        <div class="kpi-row">
          <div class="kpi-card"><div class="kpi-t">Conversión</div><div class="kpi-v">4.82% <span style="font-size:12px;color:#10B981;">↑</span></div></div>
          <div class="kpi-card"><div class="kpi-t">Ticket Medio</div><div class="kpi-v" style="color:#F59E0B;">$24.50 USD</div></div>
        </div>
        <div class="tx-sect"><div class="tx-hdr">Actividad en Tiempo Real</div>{tx_html}</div>
      </div>
    </div>
    <div class="home-indicator"></div>
    </body></html>"""
