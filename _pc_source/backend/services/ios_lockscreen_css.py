"""CSS del lockscreen iOS 17.5.

Construido contra capturas reales de iPhone 15 Pro (738x1600 escalado a 393x852).
Las proporciones salen de medir la referencia, no de estimar.
"""

LOCK_CSS = """
*{box-sizing:border-box;margin:0;padding:0;font-family:"SF Pro Display",-apple-system,BlinkMacSystemFont,"Inter",sans-serif;-webkit-font-smoothing:antialiased}
html,body{width:393px;height:852px;overflow:hidden}
body{__BG__ color:#fff;position:relative;display:flex;flex-direction:column}
body::after{content:"";position:absolute;inset:0;pointer-events:none;opacity:.055;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 200'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");mix-blend-mode:overlay}

/* ---- barra de estado ---- */
.status-bar{height:54px;padding:16px 26px 0 26px;display:flex;justify-content:space-between;align-items:flex-start;position:relative;z-index:5}
.carrier{font-size:16px;font-weight:600;letter-spacing:-.2px;color:rgba(255,255,255,.96)}
.status-icons{display:flex;align-items:center;gap:5px}
.sig{width:18px;height:12px;display:block}
.wifi{width:17px;height:12px;display:block}
.battery{width:27px;height:13px;border-radius:4px;background:rgba(255,255,255,.92);display:flex;align-items:center;justify-content:center;position:relative;margin-left:1px}
.battery span{font-size:9.5px;font-weight:700;color:#000;letter-spacing:-.3px;line-height:1}
.battery::after{content:"";position:absolute;right:-2.5px;top:4px;width:1.8px;height:5px;border-radius:0 2px 2px 0;background:rgba(255,255,255,.55)}

/* ---- candado, fecha y reloj ---- */
.lock-block{padding:44px 20px 0;text-align:center;position:relative;z-index:5}
.now-line{display:flex;align-items:center;justify-content:center;gap:7px;font-size:15.5px;font-weight:600;letter-spacing:-.2px;color:rgba(255,255,255,.94);text-shadow:0 1px 5px rgba(0,0,0,.45);min-height:20px}
.now-line svg{width:15px;height:15px;fill:currentColor;opacity:.95;flex-shrink:0}
.now-line .track{max-width:250px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.clock{font-size:114px;font-weight:700;line-height:.94;letter-spacing:-3.6px;color:rgba(255,255,255,.94);text-shadow:0 4px 26px rgba(0,0,0,.38);margin-top:3px;font-feature-settings:"tnum" 1;white-space:nowrap}
.widgets-row{display:flex;justify-content:center;align-items:center;gap:9px;margin-top:15px}
.widget-rect{width:160px;height:70px;border-radius:21px;background:rgba(22,26,36,.52);border:.5px solid rgba(255,255,255,.16);backdrop-filter:blur(26px) saturate(160%);padding:8px 12px;text-align:left}
.w-badge{font-size:9px;font-weight:700;letter-spacing:.55px;color:rgba(255,255,255,.7);display:flex;align-items:center;gap:4px}
.w-dot{width:5px;height:5px;border-radius:50%;background:#10B981}
.w-main{font-size:15.5px;font-weight:800;color:#fff;margin-top:1px;line-height:1.1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.w-sub{font-size:10px;font-weight:600;color:#6ee7b7;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.widget-circ{width:70px;height:70px;border-radius:50%;background:rgba(22,26,36,.52);border:.5px solid rgba(255,255,255,.16);backdrop-filter:blur(26px) saturate(160%);display:flex;align-items:center;justify-content:center;position:relative}
.widget-circ svg{width:52px;height:52px;transform:rotate(-90deg)}
.widget-circ span{position:absolute;font-size:12px;font-weight:800}

/* ---- centro de notificaciones ---- */
.notif-section{padding:0 16px;margin-top:auto;margin-bottom:10px;position:relative;z-index:5}
.notif-hdr{display:flex;justify-content:space-between;align-items:center;padding:0 6px 8px;font-size:18px;font-weight:600;letter-spacing:-.35px;color:rgba(255,255,255,.96);text-shadow:0 1px 6px rgba(0,0,0,.35)}
.close-btn{width:26px;height:26px;border-radius:50%;background:rgba(255,255,255,.22);backdrop-filter:blur(12px);display:flex;align-items:center;justify-content:center}
.close-btn svg{width:11px;height:11px;stroke:#fff;stroke-width:2.4;fill:none}
.notif-card{width:361px;margin:0 auto;background:rgba(24,26,34,.58);backdrop-filter:blur(34px) saturate(180%);border:.5px solid rgba(255,255,255,.14);border-radius:22px;padding:11px 13px;display:flex;align-items:center;gap:11px;box-shadow:0 12px 34px rgba(0,0,0,.42);margin-bottom:7px}
.icon-squircle{width:34px;height:34px;border-radius:8.5px;display:flex;align-items:center;justify-content:center;flex-shrink:0;overflow:hidden}
.icon-squircle img{width:100%;height:100%;object-fit:cover}
.gumroad-bg{background:#FF90E8}
.hotmart-bg{background:linear-gradient(135deg,#FF6A3D 0%,#E83E14 100%)}
.glyph{width:23px;height:23px;border-radius:50%;background:#000;color:#FF90E8;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:900}
.notif-body{flex:1;min-width:0}
.notif-title-row{display:flex;justify-content:space-between;align-items:baseline;gap:8px}
.notif-title{font-size:15px;font-weight:600;color:#fff;letter-spacing:-.15px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.notif-time{font-size:11.5px;font-weight:400;color:rgba(255,255,255,.55);flex-shrink:0}
.notif-text{font-size:14.5px;font-weight:400;color:rgba(255,255,255,.92);line-height:1.2;letter-spacing:-.1px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;margin-top:1px}
.tail-1{height:9px;margin:-11px 14px 0;background:rgba(24,26,34,.4);border-radius:0 0 18px 18px}

/* ---- acciones inferiores ---- */
.bottom-actions{padding:4px 30px 16px;display:flex;justify-content:space-between;align-items:center;position:relative;z-index:5}
.action-circle{width:72px;height:72px;border-radius:50%;background:rgba(22,24,32,.46);border:.5px solid rgba(255,255,255,.16);backdrop-filter:blur(24px);display:flex;align-items:center;justify-content:center}
.action-circle svg{width:27px;height:27px;fill:#fff;opacity:.96}
.home-indicator{width:134px;height:5px;background:rgba(255,255,255,.96);border-radius:100px;margin:0 auto 6px}
"""


def build_lockscreen_css(background: str, font_face: str) -> str:
    return font_face + LOCK_CSS.replace("__BG__", background)
