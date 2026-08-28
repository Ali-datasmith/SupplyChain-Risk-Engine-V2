"""Supply Chain Risk Engine V2 — premium B2B design system."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

DESIGN_TOKENS: dict[str, str] = {
    "bg_page": "#0B1220",
    "bg_card": "#111C30",
    "bg_elevated": "#1E2A44",
    "border": "#1E2A44",
    "border_hover": "#22D3EE",
    "accent": "#22D3EE",
    "accent_2": "#818CF8",
    "text_1": "#E6EDF6",
    "text_2": "#94A3B8",
    "text_3": "#64748B",
    "grid": "#1E2A44",
    "font_ui": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
    "font_mono": "'JetBrains Mono', 'SF Mono', Consolas, monospace",
}

RISK_COLORS: dict[str, str] = {
    "LOW": "#34D399",
    "MEDIUM": "#FACC15",
    "HIGH": "#8B5CF6",
    "CRITICAL": "#F43F5E",
}

RISK_RGB: dict[str, tuple[int, int, int]] = {
    "LOW": (52, 211, 153),
    "MEDIUM": (250, 204, 21),
    "HIGH": (139, 92, 246),
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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

/* --- BASE LAYOUT --- */
html, body, .stApp {
    background-color: #0B1220 !important;
    color: #E6EDF6;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    -webkit-font-smoothing: antialiased;
}
.main .block-container { padding-top: 2rem !important; padding-bottom: 4rem !important; max-width: 1600px !important; }
h1 { font-weight: 800 !important; letter-spacing: -0.02em !important; color: #E6EDF6 !important; }
h2 { font-weight: 700 !important; color: #E6EDF6 !important; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 8px; }
h3 { font-weight: 600 !important; color: #E6EDF6 !important; }
p, span, div, label { color: #E6EDF6; }
hr { border-color: rgba(255,255,255,0.08) !important; margin: 1.5rem 0 !important; }

/* --- GLASSMORPHISM CARDS / METRICS --- */
.obs-card, .glass-card, [data-testid="stMetric"] {
    background: rgba(17, 28, 48, 0.6);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(30, 42, 68, 0.8);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    margin-bottom: 1.5rem;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.obs-card::before, .glass-card::before {
    content: ""; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, #22D3EE, transparent);
    opacity: 0.8;
}
.obs-card:hover, .glass-card:hover, [data-testid="stMetric"]:hover {
    border-color: rgba(34, 211, 238, 0.4);
    box-shadow: 0 8px 32px 0 rgba(34, 211, 238, 0.15);
    transform: translateY(-2px);
}
[data-testid="stMetricLabel"] { color: #94A3B8 !important; font-family: 'JetBrains Mono', monospace !important; font-size: 11px !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.08em !important; }
[data-testid="stMetricValue"] { color: #E6EDF6 !important; font-weight: 800 !important; font-size: 32px !important; }
[data-testid="stMetricDelta"] { font-family: 'JetBrains Mono', monospace !important; font-size: 13px !important; }

/* --- KPI VALUES: theme-matched accent colors, not white --- */
[data-testid="stHorizontalBlock"] > div:nth-child(1) [data-testid="stMetricLabel"] { color: rgba(34, 211, 238, 0.80) !important; }
[data-testid="stHorizontalBlock"] > div:nth-child(1) [data-testid="stMetricValue"] { color: #22D3EE !important; text-shadow: 0 0 14px rgba(34, 211, 238, 0.35); }
[data-testid="stHorizontalBlock"] > div:nth-child(2) [data-testid="stMetricLabel"] { color: rgba(129, 140, 248, 0.85) !important; }
[data-testid="stHorizontalBlock"] > div:nth-child(2) [data-testid="stMetricValue"] { color: #818CF8 !important; text-shadow: 0 0 14px rgba(129, 140, 248, 0.35); }
[data-testid="stHorizontalBlock"] > div:nth-child(3) [data-testid="stMetricLabel"] { color: rgba(139, 92, 246, 0.85) !important; }
[data-testid="stHorizontalBlock"] > div:nth-child(3) [data-testid="stMetricValue"] { color: #8B5CF6 !important; text-shadow: 0 0 14px rgba(139, 92, 246, 0.40); }
[data-testid="stHorizontalBlock"] > div:nth-child(4) [data-testid="stMetricLabel"] { color: rgba(244, 63, 94, 0.85) !important; }
[data-testid="stHorizontalBlock"] > div:nth-child(4) [data-testid="stMetricValue"] { color: #F43F5E !important; text-shadow: 0 0 14px rgba(244, 63, 94, 0.40); }

/* --- CUSTOM KPI --- */
.obs-kpi-label { font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: #94A3B8; margin-bottom: 8px; }
.obs-kpi-value { font-family: 'Inter', sans-serif; font-size: 32px; font-weight: 800; color: #E6EDF6; line-height: 1; margin-bottom: 12px; }
.obs-kpi-delta { display: inline-block; font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 700; padding: 4px 10px; border-radius: 6px; }
.obs-kpi-delta.up { background: rgba(52, 211, 153, 0.15); color: #34D399; }
.obs-kpi-delta.down { background: rgba(244, 63, 94, 0.15); color: #F43F5E; }
.obs-kpi-delta.neutral { background: rgba(148, 163, 184, 0.12); color: #94A3B8; }

/* --- TABS / SIDEBAR / TABLES / CONTROLS --- */
.stTabs [data-baseweb="tab-list"] { gap: 8px; background: transparent; border-bottom: 1px solid rgba(255, 255, 255, 0.08); }
.stTabs [data-baseweb="tab"] { background: rgba(17, 28, 48, 0.4); color: #94A3B8; padding: 10px 24px; border-radius: 8px 8px 0 0; font-family: 'Inter', sans-serif; font-weight: 600; border: 1px solid transparent; }
.stTabs [aria-selected="true"] { background: rgba(34, 211, 238, 0.1) !important; color: #22D3EE !important; border: 1px solid rgba(34, 211, 238, 0.3) !important; border-bottom: 1px solid #0B1220 !important; }
section[data-testid="stSidebar"] { background: rgba(11, 18, 32, 0.8) !important; backdrop-filter: blur(20px); border-right: 1px solid rgba(255, 255, 255, 0.05) !important; }
.stDataFrame { border: 1px solid rgba(30, 42, 68, 0.8) !important; border-radius: 16px !important; overflow: hidden !important; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); }
.stButton > button { background: linear-gradient(135deg, #22D3EE 0%, #818CF8 100%); color: white; border: none; border-radius: 8px; font-family: 'Inter', sans-serif; font-weight: 600; padding: 10px 24px; transition: all 0.2s ease; box-shadow: 0 4px 12px rgba(34, 211, 238, 0.2); }
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(34, 211, 238, 0.4); }
.stButton > button[kind="secondary"] { background: rgba(17, 28, 48, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); box-shadow: none; }
.stTextInput > div > div, .stSelectbox > div > div, .stMultiSelect > div > div, .stTextArea > div > div { background: rgba(11, 18, 32, 0.6) !important; border: 1px solid rgba(30, 42, 68, 0.8) !important; border-radius: 8px !important; color: #E6EDF6 !important; }
.stFileUploader { background: rgba(11, 18, 32, 0.4) !important; border: 2px dashed rgba(34, 211, 238, 0.4) !important; border-radius: 16px !important; }
.stExpander { background: rgba(17, 28, 48, 0.4) !important; border: 1px solid rgba(30, 42, 68, 0.8) !important; border-radius: 16px !important; backdrop-filter: blur(8px); }

/* --- AI NARRATIVES: indigo/cyan body text, not white --- */
[data-testid="stExpander"] p { color: #A5B4FC !important; }
[data-testid="stExpander"] p strong, [data-testid="stExpander"] code { color: #67E8F9 !important; }

/* --- INTEL FEED / DIGEST: themed text tones --- */
[data-testid="stVerticalBlockBorderWrapper"] p { color: #94A3B8 !important; }
[data-testid="stVerticalBlockBorderWrapper"] p strong { color: #67E8F9 !important; }
[data-testid="stVerticalBlockBorderWrapper"] a { color: #22D3EE !important; }
[data-testid="stVerticalBlockBorderWrapper"] li { color: #A5B4FC !important; }

/* --- CAPTIONS (weather condition, meta, confidence) --- */
[data-testid="stCaptionContainer"] { color: rgba(34, 211, 238, 0.75) !important; }

/* --- MAP PICTURE FRAME --- */
.map-frame {
    position: relative;
    margin: 10px 0 8px;
    padding: 10px;
    background: linear-gradient(160deg, #111C30 0%, #0B1220 100%);
    border: 1px solid rgba(34, 211, 238, 0.35);
    border-radius: 18px;
    box-shadow: 0 24px 60px rgba(0, 0, 0, 0.55), inset 0 1px 0 rgba(255,255,255,0.06);
}
.map-frame::before {
    content: "";
    position: absolute;
    inset: 5px;
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 12px;
    pointer-events: none;
    z-index: 1;
}
.map-frame iframe { border-radius: 10px; }

/* --- REQUIRED TEST CLASSES --- */
.obs-micro { font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; display: block; margin-bottom: 12px; }
.obs-empty { border: 1px dashed rgba(30, 42, 68, 0.8); border-radius: 16px; padding: 44px 24px; text-align: center; color: #64748B; font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 600; background: rgba(17, 28, 48, 0.4); }
.obs-brand { display: flex; align-items: baseline; justify-content: space-between; padding: 14px 0 12px; border-bottom: 1px solid rgba(255,255,255,0.08); font-family: 'Inter', sans-serif; font-size: 24px; font-weight: 800; color: #E6EDF6; }
.obs-ops { display: flex; flex-wrap: wrap; gap: 22px; padding: 9px 2px; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 20px; font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 600; text-transform: uppercase; color: #64748B; }
.obs-pill { display: inline-flex; align-items: center; gap: 8px; font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; padding: 5px 11px; border-radius: 6px; border: 1px solid rgba(30, 42, 68, 0.8); color: #94A3B8; margin-right: 6px; }
.obs-pill .dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.obs-pill.low { background: rgba(52, 211, 153, 0.15); color: #34D399; border-color: rgba(52, 211, 153, 0.4); }
.obs-pill.medium { background: rgba(250, 204, 21, 0.15); color: #FACC15; border-color: rgba(250, 204, 21, 0.4); }
.obs-pill.high { background: rgba(139, 92, 246, 0.15); color: #8B5CF6; border-color: rgba(139, 92, 246, 0.4); }
.obs-pill.critical { background: rgba(244, 63, 94, 0.15); color: #F43F5E; border-color: rgba(244, 63, 94, 0.4); box-shadow: 0 0 12px rgba(244, 63, 94, 0.3); }

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #0B1220; }
::-webkit-scrollbar-thumb { background: #1E2A44; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #22D3EE; }
</style>
"""

def kpi_card(label: str, value: str | float | int, delta: str | None = None, delta_dir: str = "neutral", accent: str = "cyan") -> str:
    accent_class = ""
    if accent in ("indigo", "risk-low", "risk-medium", "risk-high", "risk-critical"):
        accent_class = accent
    elif accent == "risk_low": accent_class = "risk-low"
    elif accent == "risk_medium": accent_class = "risk-medium"
    elif accent == "risk_high": accent_class = "risk-high"
    elif accent == "risk_critical": accent_class = "risk-critical"
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

def legend_html() -> str:
    """Static severity legend rendered above the framed map."""
    return (
        '<div style="margin:6px 0 2px;">'
        + status_pill("CRITICAL")
        + '<span class="obs-micro" style="display:inline;margin:0 14px 0 2px;">&ge; 0.85</span>'
        + status_pill("HIGH")
        + '<span class="obs-micro" style="display:inline;margin:0 14px 0 2px;">&ge; 0.70</span>'
        + status_pill("MEDIUM")
        + '<span class="obs-micro" style="display:inline;margin:0 14px 0 2px;">&ge; 0.40</span>'
        + status_pill("LOW")
        + '<span class="obs-micro" style="display:inline;margin:0 0 0 2px;">&lt; 0.40</span>'
        + '</div>'
    )

def brand_bar() -> str:
    return (
        '<div class="obs-brand">'
        '<span class="obs-brand-word"><span class="mark">◆</span> Supply Chain Risk Engine V2</span>'
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
