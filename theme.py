"""Supply Chain Risk Engine V2 — premium B2B design system (OBSIDIAN PRIME)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

DESIGN_TOKENS: dict[str, str] = {
    "bg_page": "#04060C",
    "bg_card": "#0B1220",
    "bg_elevated": "#111A2E",
    "border": "#1E2A44",
    "border_hover": "#22D3EE",
    "accent": "#22D3EE",
    "accent_2": "#A855F7",
    "text_1": "#F4F7FB",
    "text_2": "#9AA7BD",
    "text_3": "#5D6B84",
    "grid": "#16233C",
    "font_ui": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
    "font_mono": "'JetBrains Mono', 'SF Mono', Consolas, monospace",
}

RISK_COLORS: dict[str, str] = {
    "LOW": "#34D399",
    "MEDIUM": "#FACC15",
    "HIGH": "#A78BFA",
    "CRITICAL": "#F43F5E",
}

RISK_RGB: dict[str, tuple[int, int, int]] = {
    "LOW": (52, 211, 153),
    "MEDIUM": (250, 204, 21),
    "HIGH": (167, 139, 250),
    "CRITICAL": (244, 63, 94),
}

def risk_band(value: float) -> str:
    if value >= 0.85:
        return "CRITICAL"
    if value >= 0.70:
        return "HIGH"
    if value >= 0.40:
        return "MEDIUM"
    return "LOW"

def get_plotly_layout() -> dict[str, Any]:
    """Plotly layout defaults. Each chart sets its own title."""
    return {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": DESIGN_TOKENS["font_ui"], "color": DESIGN_TOKENS["text_1"], "size": 12},
        "xaxis": {
            "gridcolor": DESIGN_TOKENS["grid"],
            "zerolinecolor": DESIGN_TOKENS["grid"],
            "linecolor": DESIGN_TOKENS["grid"],
            "color": DESIGN_TOKENS["text_2"],
            "tickfont": {"size": 11},
        },
        "yaxis": {
            "gridcolor": DESIGN_TOKENS["grid"],
            "zerolinecolor": DESIGN_TOKENS["grid"],
            "linecolor": DESIGN_TOKENS["grid"],
            "color": DESIGN_TOKENS["text_2"],
            "tickfont": {"size": 11},
        },
        "margin": {"l": 0, "r": 0, "t": 44, "b": 36},
        "legend": {"bgcolor": "rgba(0,0,0,0)", "font": {"color": DESIGN_TOKENS["text_2"], "size": 11}},
        "colorway": [
            DESIGN_TOKENS["accent"],
            DESIGN_TOKENS["accent_2"],
            RISK_COLORS["HIGH"],
            RISK_COLORS["MEDIUM"],
            RISK_COLORS["LOW"],
        ],
    }

def inject_theme_css() -> str:
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap');

/* --- DEEP-SPACE AMBIENT BACKGROUND --- */
html, body, .stApp, [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(1200px 700px at 85% -10%, rgba(168, 85, 247, 0.14), transparent 60%),
        radial-gradient(1000px 600px at -10% 0%, rgba(34, 211, 238, 0.12), transparent 55%),
        radial-gradient(1600px 900px at 50% 120%, rgba(59, 7, 100, 0.25), transparent 60%),
        repeating-linear-gradient(0deg, rgba(148,163,184,0.04) 0 1px, transparent 1px 48px),
        repeating-linear-gradient(90deg, rgba(148,163,184,0.04) 0 1px, transparent 1px 48px),
        #04060C !important;
    color: #F4F7FB;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    -webkit-font-smoothing: antialiased;
}
::selection { background: rgba(34, 211, 238, 0.35); color: #F4F7FB; }
.main .block-container { padding-top: 1.75rem !important; padding-bottom: 4rem !important; max-width: 1600px !important; }
header[data-testid="stHeader"] { background: transparent !important; }
h1 { font-weight: 800 !important; letter-spacing: -0.03em !important; color: #F4F7FB !important; }
h2 { font-weight: 700 !important; color: #F4F7FB !important; border-bottom: 1px solid rgba(148,163,184,0.15); padding-bottom: 8px; }
h3 { font-weight: 600 !important; color: #F4F7FB !important; }
p, span, div, label { color: #F4F7FB; }
hr { border-color: rgba(148,163,184,0.15) !important; }

/* --- GLASS CARDS / METRICS --- */
.obs-card, .glass-card, [data-testid="stMetric"], [data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(160deg, rgba(17, 26, 46, 0.85), rgba(7, 11, 20, 0.9));
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1px solid rgba(34, 211, 238, 0.16);
    border-radius: 18px;
    padding: 22px;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.55), inset 0 1px 0 rgba(255,255,255,0.07);
    position: relative;
    overflow: hidden;
    transition: border-color .25s ease, box-shadow .25s ease, transform .25s ease;
}
.obs-card::before, .glass-card::before, [data-testid="stMetric"]::before {
    content: ""; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #22D3EE, #A855F7);
    opacity: 0.9;
}
.obs-card:hover, .glass-card:hover, [data-testid="stMetric"]:hover {
    border-color: rgba(34, 211, 238, 0.45);
    box-shadow: 0 24px 60px rgba(0,0,0,0.6), 0 0 30px rgba(34,211,238,0.12), inset 0 1px 0 rgba(255,255,255,0.08);
    transform: translateY(-2px);
}
[data-testid="stMetricLabel"] { color: #7C8BA6 !important; font-family: 'JetBrains Mono', monospace !important; font-size: 11px !important; font-weight: 700 !important; text-transform: uppercase !important; letter-spacing: 0.12em !important; }
[data-testid="stMetricValue"] {
    font-weight: 800 !important; font-size: 32px !important;
    background: linear-gradient(120deg, #7DF3FF 0%, #22D3EE 45%, #A855F7 110%);
    -webkit-background-clip: text; background-clip: text; color: transparent !important;
    filter: drop-shadow(0 0 14px rgba(34,211,238,0.35));
}
[data-testid="stHorizontalBlock"] > div:nth-child(2) [data-testid="stMetricValue"] { background: linear-gradient(120deg, #C4B5FD, #A855F7); -webkit-background-clip: text; background-clip: text; filter: drop-shadow(0 0 14px rgba(168,85,247,0.35)); }
[data-testid="stHorizontalBlock"] > div:nth-child(3) [data-testid="stMetricValue"] { background: linear-gradient(120deg, #DDD6FE, #A78BFA); -webkit-background-clip: text; background-clip: text; filter: drop-shadow(0 0 14px rgba(167,139,250,0.4)); }
[data-testid="stHorizontalBlock"] > div:nth-child(4) [data-testid="stMetricValue"] { background: linear-gradient(120deg, #FDA4AF, #F43F5E); -webkit-background-clip: text; background-clip: text; filter: drop-shadow(0 0 16px rgba(244,63,94,0.45)); }
[data-testid="stMetricDelta"] { font-family: 'JetBrains Mono', monospace !important; font-size: 12px !important; }

/* --- OBS KPI --- */
.obs-kpi-label { font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.12em; color: #7C8BA6; margin-bottom: 8px; }
.obs-kpi-value { font-family: 'Inter', sans-serif; font-size: 32px; font-weight: 800; color: #F4F7FB; line-height: 1; margin-bottom: 12px; }
.obs-kpi-delta { display: inline-block; font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 700; padding: 4px 10px; border-radius: 6px; }
.obs-kpi-delta.up { background: rgba(52, 211, 153, 0.15); color: #34D399; }
.obs-kpi-delta.down { background: rgba(244, 63, 94, 0.15); color: #F43F5E; }
.obs-kpi-delta.neutral { background: rgba(148, 163, 184, 0.12); color: #9AA7BD; }

/* --- TABS --- */
.stTabs [data-baseweb="tab-list"] { gap: 8px; background: transparent; border-bottom: 1px solid rgba(148,163,184,0.15); }
.stTabs [data-baseweb="tab"] { background: rgba(11, 18, 32, 0.5); color: #7C8BA6; padding: 10px 24px; border-radius: 10px 10px 0 0; font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 12px; text-transform: uppercase; letter-spacing: 0.1em; border: 1px solid transparent; }
.stTabs [data-baseweb="tab"]:hover { color: #C9F6FF; }
.stTabs [aria-selected="true"] { background: rgba(34, 211, 238, 0.10) !important; color: #7DF3FF !important; border: 1px solid rgba(34, 211, 238, 0.35) !important; border-bottom: 2px solid #22D3EE !important; text-shadow: 0 0 12px rgba(34,211,238,0.6); }

/* --- SIDEBAR / TABLES / CONTROLS --- */
section[data-testid="stSidebar"] { background: rgba(4, 6, 12, 0.9) !important; backdrop-filter: blur(20px); border-right: 1px solid rgba(34,211,238,0.12) !important; }
.stDataFrame { border: 1px solid rgba(34,211,238,0.2) !important; border-radius: 16px !important; overflow: hidden !important; box-shadow: 0 20px 50px rgba(0,0,0,0.5); }
.stButton > button {
    background: linear-gradient(100deg, #06B6D4 0%, #22D3EE 35%, #7C3AED 100%);
    color: white; border: none; border-radius: 10px; font-family: 'Inter', sans-serif; font-weight: 700;
    padding: 10px 24px; letter-spacing: 0.02em;
    box-shadow: 0 8px 28px rgba(34,211,238,0.28), inset 0 1px 0 rgba(255,255,255,0.3);
    transition: all 0.2s ease;
}
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 12px 36px rgba(124,58,237,0.4), inset 0 1px 0 rgba(255,255,255,0.35); }
.stButton > button[kind="secondary"] { background: rgba(17, 26, 46, 0.7); border: 1px solid rgba(34,211,238,0.25); box-shadow: none; }
.stTextInput > div > div, .stSelectbox > div > div, .stMultiSelect > div > div, .stTextArea > div > div { background: rgba(7, 11, 20, 0.7) !important; border: 1px solid rgba(34,211,238,0.2) !important; border-radius: 10px !important; color: #F4F7FB !important; }
span[data-baseweb="tag"] { background: rgba(34,211,238,0.14) !important; border: 1px solid rgba(34,211,238,0.4) !important; color: #7DF3FF !important; border-radius: 8px !important; }
.stFileUploader { background: rgba(7, 11, 20, 0.6) !important; border: 2px dashed rgba(34,211,238,0.4) !important; border-radius: 18px !important; }
.stExpander { background: rgba(11, 18, 32, 0.6) !important; border: 1px solid rgba(148,163,184,0.18) !important; border-radius: 16px !important; backdrop-filter: blur(12px); }
[data-testid="stExpander"] p { color: #A5B4FC !important; }
[data-testid="stExpander"] p strong { color: #67E8F9 !important; }
[data-testid="stCaptionContainer"] { color: rgba(125, 211, 252, 0.75) !important; }

/* --- MAP PICTURE FRAME --- */
.map-frame {
    position: relative; margin: 14px 0 10px; padding: 12px; border-radius: 20px;
    background: linear-gradient(160deg, rgba(34,211,238,0.10), rgba(11,18,32,0.95) 35%, rgba(168,85,247,0.12));
    border: 1px solid rgba(34,211,238,0.3);
    box-shadow: 0 30px 80px rgba(0,0,0,0.65), inset 0 1px 0 rgba(255,255,255,0.07);
}
.map-frame::before { content: ""; position: absolute; inset: 6px; border: 1px solid rgba(148,163,184,0.18); border-radius: 14px; pointer-events: none; z-index: 1; }
.map-frame iframe { border-radius: 12px; }

/* --- BRAND / OPS / LEGEND / PILLS / MICRO / EMPTY --- */
.obs-legend { margin: 10px 0 6px; }
.obs-micro { font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.18em; color: #5D6B84; display: block; margin-bottom: 12px; }
.obs-empty { border: 1px dashed rgba(34,211,238,0.3); border-radius: 18px; padding: 44px 24px; text-align: center; color: #7C8BA6; font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; letter-spacing: 0.12em; background: rgba(11, 18, 32, 0.5); }
.obs-brand { display: flex; align-items: baseline; justify-content: space-between; padding: 16px 0 14px; border-bottom: 1px solid rgba(148,163,184,0.15); font-family: 'JetBrains Mono', monospace; font-size: 22px; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; color: #F4F7FB; }
.obs-brand .mark { background: linear-gradient(120deg, #22D3EE, #A855F7); -webkit-background-clip: text; background-clip: text; color: transparent; filter: drop-shadow(0 0 16px rgba(34,211,238,0.6)); }
.obs-ops { display: flex; flex-wrap: wrap; gap: 22px; padding: 10px 2px; border-bottom: 1px solid rgba(148,163,184,0.15); margin-bottom: 22px; font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase; color: #5D6B84; }
.obs-ops b { color: #9AA7BD; }
@keyframes obsPulse { 0%,100% { box-shadow: 0 0 0 0 rgba(52,211,153,0.5);} 50% { box-shadow: 0 0 0 6px rgba(52,211,153,0);} }
.obs-ops .dot { display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: #34D399; margin-right: 7px; vertical-align: middle; animation: obsPulse 2s infinite; }
.obs-pill { display: inline-flex; align-items: center; gap: 8px; font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase; padding: 6px 12px; border-radius: 8px; border: 1px solid rgba(148,163,184,0.2); color: #9AA7BD; margin-right: 8px; }
.obs-pill .dot { width: 7px; height: 7px; border-radius: 50%; background: currentColor; }
.obs-pill.low { background: rgba(52, 211, 153, 0.14); color: #34D399; border-color: rgba(52, 211, 153, 0.45); }
.obs-pill.low .dot { box-shadow: 0 0 10px #34D399; }
.obs-pill.medium { background: rgba(250, 204, 21, 0.14); color: #FACC15; border-color: rgba(250, 204, 21, 0.45); }
.obs-pill.medium .dot { box-shadow: 0 0 10px #FACC15; }
.obs-pill.high { background: rgba(167, 139, 250, 0.16); color: #A78BFA; border-color: rgba(167, 139, 250, 0.5); }
.obs-pill.high .dot { box-shadow: 0 0 10px #A78BFA; }
.obs-pill.critical { background: rgba(244, 63, 94, 0.16); color: #F43F5E; border-color: rgba(244, 63, 94, 0.55); }
.obs-pill.critical .dot { box-shadow: 0 0 12px #F43F5E; }

/* --- SCROLLBARS --- */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #04060C; }
::-webkit-scrollbar-thumb { background: #1E2A44; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #22D3EE; }
</style>
"""

def kpi_card(label: str, value: str | float, delta: str | None = None, delta_dir: str = "neutral", accent: str = "cyan") -> str:
    accent_class = ""
    if accent in ("indigo", "risk-low", "risk-medium", "risk-high", "risk-critical"):
        accent_class = accent
    elif accent == "risk_low":
        accent_class = "risk-low"
    elif accent == "risk_medium":
        accent_class = "risk-medium"
    elif accent == "risk_high":
        accent_class = "risk-high"
    elif accent == "risk_critical":
        accent_class = "risk-critical"
    delta_html = f'<div class="obs-kpi-delta {delta_dir}">{delta}</div>' if delta else ""
    return (
        f'<div class="obs-card {accent_class}">'
        f'<div class="obs-kpi-label">{label}</div>'
        f'<div class="obs-kpi-value">{value}</div>'
        f"{delta_html}</div>"
    )

def status_pill(level: Any) -> str:
    raw = getattr(level, "value", str(level))
    key = str(raw).upper()
    cls = key.lower() if key in ("LOW", "MEDIUM", "HIGH", "CRITICAL") else ""
    return f'<span class="obs-pill {cls}"><span class="dot"></span>{key}</span>'

def legend_html(counts: dict[str, int] | None = None) -> str:
    """Severity legend. Accepts optional per-band counts; safe to call with no args."""
    parts = []
    for band in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        n = (counts or {}).get(band)
        suffix = f" · {int(n):,}" if n is not None else ""
        parts.append(
            f'<span class="obs-pill {band.lower()}"><span class="dot"></span>{band}{suffix}</span>'
        )
    return '<div class="obs-legend">' + "".join(parts) + "</div>"

def brand_bar() -> str:
    return (
        '<div class="obs-brand">'
        '<span><span class="mark">◆</span> Supply Chain Risk Engine V2</span>'
        '<span class="obs-micro" style="margin:0;">Enterprise Edition</span>'
        '</div>'
    )

def ops_strip(*, env: str = "PROD", version: str = "V2.1", now: datetime | None = None) -> str:
    ts = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        '<div class="obs-ops">'
        f'<span><span class="dot"></span>ENV <b>{env}</b></span>'
        f'<span>BUILD <b>{version}</b></span>'
        f'<span>SYNC <b>{ts}</b></span>'
        '<span>STATUS <b style="color:#34D399;">OPERATIONAL</b></span>'
        '</div>'
    )
