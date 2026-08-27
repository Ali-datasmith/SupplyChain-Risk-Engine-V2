"""Supply Chain Risk Engine V2 — Premium B2B Command Center Design System."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

DESIGN_TOKENS: dict[str, str] = {
    "bg_page": "#03050A",
    "bg_card": "#0A0F1C",
    "bg_elevated": "#111827",
    "border": "rgba(255, 255, 255, 0.06)",
    "border_hover": "#00E5FF",
    "accent": "#00E5FF",
    "accent_2": "#7C3AED",
    "text_1": "#F8FAFC",
    "text_2": "#94A3B8",
    "text_3": "#64748B",
    "grid": "rgba(255, 255, 255, 0.04)",
    "font_ui": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
    "font_mono": "'JetBrains Mono', 'SF Mono', Consolas, monospace",
}

RISK_COLORS: dict[str, str] = {
    "LOW": "#10B981",
    "MEDIUM": "#F59E0B",
    "HIGH": "#F97316",
    "CRITICAL": "#EF4444",
}

RISK_RGB: dict[str, tuple[int, int, int]] = {
    "LOW": (16, 185, 129),
    "MEDIUM": (245, 158, 11),
    "HIGH": (249, 115, 22),
    "CRITICAL": (239, 68, 68),
}

def risk_band(value: float) -> str:
    if value >= 0.85: return "CRITICAL"
    if value >= 0.70: return "HIGH"
    if value >= 0.40: return "MEDIUM"
    return "LOW"

def get_plotly_layout() -> dict[str, Any]:
    return {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": DESIGN_TOKENS["font_ui"], "color": DESIGN_TOKENS["text_1"], "size": 12},
        "xaxis": {"gridcolor": DESIGN_TOKENS["grid"], "zerolinecolor": DESIGN_TOKENS["grid"], "linecolor": DESIGN_TOKENS["grid"], "color": DESIGN_TOKENS["text_2"], "tickfont": {"size": 11}},
        "yaxis": {"gridcolor": DESIGN_TOKENS["grid"], "zerolinecolor": DESIGN_TOKENS["grid"], "linecolor": DESIGN_TOKENS["grid"], "color": DESIGN_TOKENS["text_2"], "tickfont": {"size": 11}},
        "margin": {"l": 0, "r": 0, "t": 44, "b": 36},
        "legend": {"bgcolor": "rgba(0,0,0,0)", "font": {"color": DESIGN_TOKENS["text_2"], "size": 11}},
        "colorway": [DESIGN_TOKENS["accent"], DESIGN_TOKENS["accent_2"], RISK_COLORS["HIGH"], RISK_COLORS["MEDIUM"], RISK_COLORS["LOW"]],
    }

def inject_theme_css() -> str:
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
    --bg-deep: #03050A;
    --bg-surface: #0A0F1C;
    --bg-elevated: #111827;
    --border-subtle: rgba(255, 255, 255, 0.06);
    --accent-primary: #00E5FF;
    --accent-secondary: #7C3AED;
    --text-main: #F8FAFC;
    --text-muted: #94A3B8;
}

/* Hide default Streamlit chrome */
header[data-testid="stHeader"] { background: transparent !important; }
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }

html, body, .stApp {
    background-color: var(--bg-deep) !important;
    background-image: 
        radial-gradient(circle at 10% 20%, rgba(124, 58, 237, 0.08) 0%, transparent 40%),
        radial-gradient(circle at 90% 80%, rgba(0, 229, 255, 0.05) 0%, transparent 40%),
        linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px);
    background-size: 100% 100%, 100% 100%, 40px 40px, 40px 40px;
    color: var(--text-main);
    font-family: 'Inter', sans-serif !important;
}

.main .block-container { padding-top: 2rem !important; padding-bottom: 4rem !important; max-width: 1600px !important; }
h1, h2, h3 { color: var(--text-main) !important; letter-spacing: -0.02em !important; }
h2 { border-bottom: 1px solid var(--border-subtle); padding-bottom: 8px; }
p, span, div, label { color: var(--text-main); }

/* Glassmorphism Cards */
.glass-card, .obs-card, [data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(17, 24, 39, 0.7), rgba(10, 15, 28, 0.9));
    backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--border-subtle);
    border-radius: 16px; padding: 24px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255,255,255,0.05);
    position: relative; overflow: hidden; margin-bottom: 1.5rem;
}
.glass-card::before {
    content: ""; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0, 229, 255, 0.5), transparent);
}

/* Metrics Override */
[data-testid="stMetricLabel"] { color: var(--text-muted) !important; font-family: 'JetBrains Mono', monospace !important; font-size: 11px !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.1em !important; }
[data-testid="stMetricValue"] { color: var(--text-main) !important; font-weight: 800 !important; font-size: 32px !important; letter-spacing: -0.02em; }
[data-testid="stMetricDelta"] { font-family: 'JetBrains Mono', monospace !important; font-size: 13px !important; }

/* Premium Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 8px; background: transparent; border-bottom: 1px solid var(--border-subtle); }
.stTabs [data-baseweb="tab"] { background: transparent; color: var(--text-muted); padding: 12px 24px; border-radius: 8px 8px 0 0; font-weight: 600; font-size: 14px; border: 1px solid transparent; }
.stTabs [data-baseweb="tab"]:hover { color: var(--text-main); background: rgba(255,255,255,0.03); }
.stTabs [aria-selected="true"] { background: rgba(0, 229, 255, 0.08) !important; color: var(--accent-primary) !important; border: 1px solid rgba(0, 229, 255, 0.2) !important; border-bottom: 2px solid var(--accent-primary) !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
    color: white; border: none; border-radius: 8px; font-weight: 600; padding: 10px 24px;
    box-shadow: 0 4px 15px rgba(0, 229, 255, 0.2); transition: all 0.3s ease;
}
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0, 229, 255, 0.4); }
.stButton > button[kind="secondary"] { background: rgba(17, 24, 39, 0.8); border: 1px solid var(--border-subtle); box-shadow: none; }

/* Inputs */
.stTextInput > div > div, .stSelectbox > div > div, .stMultiSelect > div > div, .stTextArea > div > div { background: rgba(10, 15, 28, 0.8) !important; border: 1px solid var(--border-subtle) !important; border-radius: 8px !important; color: var(--text-main) !important; }
.stFileUploader { background: rgba(10, 15, 28, 0.6) !important; border: 2px dashed rgba(0, 229, 255, 0.3) !important; border-radius: 16px !important; }
.stExpander { background: rgba(17, 24, 39, 0.5) !important; border: 1px solid var(--border-subtle) !important; border-radius: 16px !important; backdrop-filter: blur(8px); }

/* Dataframes */
.stDataFrame { border: 1px solid var(--border-subtle) !important; border-radius: 12px !important; overflow: hidden !important; }

/* Sidebar */
section[data-testid="stSidebar"] { background: rgba(5, 8, 15, 0.95) !important; backdrop-filter: blur(20px); border-right: 1px solid var(--border-subtle) !important; }

/* Custom Classes */
.obs-empty { border: 1px dashed rgba(255,255,255,0.1); border-radius: 16px; padding: 44px 24px; text-align: center; color: var(--text-muted); font-family: 'JetBrains Mono', monospace; font-size: 12px; background: rgba(10, 15, 28, 0.4); }
.obs-pill { display: inline-flex; align-items: center; gap: 8px; font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 700; text-transform: uppercase; padding: 6px 12px; border-radius: 6px; border: 1px solid var(--border-subtle); color: var(--text-muted); margin-right: 8px; }
.obs-pill .dot { width: 6px; height: 6px; border-radius: 50%; }
.obs-pill.low { background: rgba(16, 185, 129, 0.1); color: #10B981; border-color: rgba(16, 185, 129, 0.3); }
.obs-pill.medium { background: rgba(245, 158, 11, 0.1); color: #F59E0B; border-color: rgba(245, 158, 11, 0.3); }
.obs-pill.high { background: rgba(249, 115, 22, 0.1); color: #F97316; border-color: rgba(249, 115, 22, 0.3); }
.obs-pill.critical { background: rgba(239, 68, 68, 0.1); color: #EF4444; border-color: rgba(239, 68, 68, 0.3); box-shadow: 0 0 12px rgba(239, 68, 68, 0.2); }

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #03050A; }
::-webkit-scrollbar-thumb { background: #1E293B; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #00E5FF; }
</style>
"""

def brand_bar() -> str:
    return """
    <div style="display: flex; align-items: center; justify-content: space-between; padding: 24px 0; border-bottom: 1px solid rgba(255,255,255,0.05); margin-bottom: 32px;">
        <div style="display: flex; align-items: center; gap: 16px;">
            <div style="width: 44px; height: 44px; background: linear-gradient(135deg, #00E5FF, #7C3AED); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: 900; color: white; box-shadow: 0 4px 20px rgba(0, 229, 255, 0.4);">◆</div>
            <div>
                <div style="font-size: 24px; font-weight: 800; letter-spacing: -0.02em; color: #F8FAFC;">Supply Chain Risk Engine <span style="color: #00E5FF;">V2</span></div>
                <div style="font-size: 12px; font-weight: 500; color: #94A3B8; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.05em;">ENTERPRISE INTELLIGENCE & THREAT COMMAND</div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 12px;">
            <span style="padding: 8px 16px; background: rgba(52, 211, 153, 0.1); color: #34D399; border: 1px solid rgba(52, 211, 153, 0.3); border-radius: 999px; font-size: 12px; font-weight: 700; font-family: 'JetBrains Mono', monospace;">● SYSTEM OPERATIONAL</span>
        </div>
    </div>
    """

def legend_html(counts: dict[str, int] | None = None) -> str:
    parts = []
    for band in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        n = (counts or {}).get(band, 0)
        parts.append(f'<span class="obs-pill {band.lower()}"><span class="dot" style="background: currentColor;"></span>{band} · {n:,}</span>')
    return '<div style="margin:16px 0 8px;">' + "".join(parts) + "</div>"

def status_pill(level: Any) -> str:
    raw = getattr(level, "value", str(level))
    key = str(raw).upper()
    cls = key.lower() if key in ("LOW", "MEDIUM", "HIGH", "CRITICAL") else ""
    return f'<span class="obs-pill {cls}"><span class="dot" style="background: currentColor;"></span>{key}</span>'
