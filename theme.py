"""
OBSIDIAN COMMAND V2 — Premium Enterprise B2B Design System.
Aggressive Streamlit overrides for high-density, terminal-grade UI.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

DESIGN_TOKENS: dict[str, str] = {
    "bg_page": "#090E17",      # Deeper, richer void black
    "bg_card": "#111827",      # Sharp slate
    "bg_elevated": "#1F2937",
    "border": "#1E293B",       # Subtle, sharp borders
    "border_hover": "#334155",
    "accent": "#06B6D4",       # Cyan-500 ( sharper, more professional than neon)
    "accent_2": "#8B5CF6",     # Violet-500
    "text_1": "#F8FAFC",       # Slate-50
    "text_2": "#94A3B8",       # Slate-400
    "text_3": "#64748B",       # Slate-500
    "grid": "#1E293B",
    "font_ui": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
    "font_mono": "'JetBrains Mono', 'SF Mono', Consolas, monospace",
}

RISK_COLORS: dict[str, str] = {
    "LOW": "#10B981",      # Emerald-500
    "MEDIUM": "#F59E0B",   # Amber-500
    "HIGH": "#F97316",     # Orange-500
    "CRITICAL": "#EF4444", # Red-500
}

def get_plotly_layout() -> dict[str, Any]:
    return {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": DESIGN_TOKENS["font_ui"], "color": DESIGN_TOKENS["text_1"], "size": 12},
        "xaxis": {"gridcolor": DESIGN_TOKENS["grid"], "zerolinecolor": DESIGN_TOKENS["grid"], "color": DESIGN_TOKENS["text_2"], "linecolor": DESIGN_TOKENS["grid"], "title_font": {"size": 11, "color": DESIGN_TOKENS["text_3"]}},
        "yaxis": {"gridcolor": DESIGN_TOKENS["grid"], "zerolinecolor": DESIGN_TOKENS["grid"], "color": DESIGN_TOKENS["text_2"], "linecolor": DESIGN_TOKENS["grid"], "title_font": {"size": 11, "color": DESIGN_TOKENS["text_3"]}},
        "margin": {"l": 0, "r": 0, "t": 40, "b": 32},
        "legend": {"bgcolor": "rgba(0,0,0,0)", "font": {"color": DESIGN_TOKENS["text_2"], "size": 11}},
        "colorway": [DESIGN_TOKENS["accent"], DESIGN_TOKENS["accent_2"], RISK_COLORS["HIGH"], RISK_COLORS["MEDIUM"], RISK_COLORS["LOW"]],
    }

def inject_theme_css() -> str:
    css_template = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── Core Density & Layout Overrides ───────────────────── */
html, body, .stApp { 
    background-color: __BG_PAGE__ !important; 
    color: __TEXT_1__; 
    font-family: __FONT_UI__; 
    -webkit-font-smoothing: antialiased;
}
.main .block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1440px !important;
}
header[data-testid="stHeader"] { background-color: __BG_PAGE__ !important; }
section[data-testid="stSidebar"] { 
    background-color: __BG_PAGE__ !important; 
    border-right: 1px solid __BORDER__ !important;
}
section[data-testid="stSidebar"] > div { padding-top: 2rem; }

/* ── Typography Hierarchy ──────────────────────────────── */
h1 { font-size: 32px !important; font-weight: 800 !important; letter-spacing: -0.04em !important; color: __TEXT_1__ !important; margin-bottom: 0.25rem !important; }
h2 { font-size: 22px !important; font-weight: 700 !important; letter-spacing: -0.02em !important; color: __TEXT_1__ !important; margin-top: 1.5rem !important; }
h3 { font-size: 13px !important; font-weight: 600 !important; color: __TEXT_3__ !important; text-transform: uppercase !important; letter-spacing: 0.08em !important; margin-bottom: 0.75rem !important; }
p, span, div, label { color: __TEXT_1__; }

.obs-mono { font-family: __FONT_MONO__; font-variant-numeric: tabular-nums; }
.obs-micro { 
    font-family: __FONT_MONO__; font-size: 10px; font-weight: 600; 
    text-transform: uppercase; letter-spacing: 0.15em; color: __TEXT_3__; 
    margin-bottom: 12px; display: block;
}

/* ── Brand Bar & Navigation ────────────────────────────── */
.obs-brand { 
    display: flex; align-items: center; justify-content: space-between; 
    padding: 12px 0 16px; border-bottom: 1px solid __BORDER__; margin-bottom: 24px; 
}
.obs-brand-word { 
    font-family: __FONT_MONO__; font-size: 14px; font-weight: 700; 
    letter-spacing: 0.15em; color: __TEXT_1__; text-transform: uppercase; 
}
.obs-brand-word .accent { color: __ACCENT__; }
.obs-brand-word .sub { color: __TEXT_3__; font-weight: 500; margin-left: 8px; }

.obs-ops { 
    display: flex; gap: 24px; padding: 10px 0; margin-bottom: 24px; 
    font-family: __FONT_MONO__; font-size: 10px; font-weight: 600; 
    letter-spacing: 0.12em; text-transform: uppercase; color: __TEXT_3__; 
}
.obs-ops b { color: __TEXT_2__; font-weight: 700; }
.obs-ops .dot { 
    display: inline-block; width: 6px; height: 6px; border-radius: 50%; 
    background: __ACCENT__; margin-right: 6px; vertical-align: middle; 
    box-shadow: 0 0 8px __ACCENT__; 
}

/* ── Cards & KPIs ──────────────────────────────────────── */
.obs-card { 
    background: linear-gradient(160deg, __BG_CARD__ 0%, #0B111E 100%); 
    border: 1px solid __BORDER__; border-radius: 12px; 
    padding: 24px; margin: 0; position: relative; overflow: hidden;
    transition: all 200ms ease;
}
.obs-card:hover { border-color: __BORDER_HOVER__; transform: translateY(-2px); }
.obs-card::before { 
    content: ""; position: absolute; top: 0; left: 0; right: 0; height: 2px; 
    background: __ACCENT__; 
}
.obs-card.indigo::before { background: __ACCENT_2__; }
.obs-card.risk-low::before { background: __RISK_LOW__; }
.obs-card.risk-medium::before { background: __RISK_MEDIUM__; }
.obs-card.risk-high::before { background: __RISK_HIGH__; }
.obs-card.risk-critical::before { background: __RISK_CRITICAL__; box-shadow: 0 0 12px __RISK_CRITICAL__; }

.obs-kpi-label { 
    font-family: __FONT_MONO__; font-size: 10px; font-weight: 700; 
    text-transform: uppercase; letter-spacing: 0.15em; color: __TEXT_3__; 
    margin-bottom: 12px; 
}
.obs-kpi-value { 
    font-family: __FONT_MONO__; font-size: 42px; font-weight: 800; 
    color: __TEXT_1__; font-variant-numeric: tabular-nums; line-height: 1; 
    margin-bottom: 8px; letter-spacing: -0.03em;
}
.obs-kpi-delta { 
    display: inline-block; font-family: __FONT_MONO__; font-size: 11px; 
    font-weight: 700; padding: 4px 10px; border-radius: 6px; letter-spacing: 0.02em; 
}
.obs-kpi-delta.up { background: rgba(16, 185, 129, 0.15); color: __RISK_LOW__; }
.obs-kpi-delta.down { background: rgba(239, 68, 68, 0.15); color: __RISK_CRITICAL__; }
.obs-kpi-delta.neutral { background: rgba(148, 163, 184, 0.1); color: __TEXT_2__; }

/* ── Pills & Badges ────────────────────────────────────── */
.obs-pill { 
    display: inline-flex; align-items: center; gap: 8px; 
    font-family: __FONT_MONO__; font-size: 11px; font-weight: 700; 
    letter-spacing: 0.08em; text-transform: uppercase; 
    padding: 6px 12px; border-radius: 6px; border: 1px solid __BORDER__; color: __TEXT_2__; 
}
.obs-pill .dot { width: 6px; height: 6px; border-radius: 50%; background: __TEXT_3__; }
.obs-pill.low { background: rgba(16, 185, 129, 0.1); color: __RISK_LOW__; border-color: rgba(16, 185, 129, 0.3); }
.obs-pill.low .dot { background: __RISK_LOW__; }
.obs-pill.medium { background: rgba(245, 158, 11, 0.1); color: __RISK_MEDIUM__; border-color: rgba(245, 158, 11, 0.3); }
.obs-pill.medium .dot { background: __RISK_MEDIUM__; }
.obs-pill.high { background: rgba(249, 115, 22, 0.1); color: __RISK_HIGH__; border-color: rgba(249, 115, 22, 0.3); }
.obs-pill.high .dot { background: __RISK_HIGH__; }
.obs-pill.critical { background: rgba(239, 68, 68, 0.15); color: __RISK_CRITICAL__; border-color: rgba(239, 68, 68, 0.4); }
.obs-pill.critical .dot { background: __RISK_CRITICAL__; box-shadow: 0 0 8px __RISK_CRITICAL__; }

/* ── Empty States ──────────────────────────────────────── */
.obs-empty { 
    border: 1px dashed __BORDER__; border-radius: 12px; padding: 48px 24px; 
    text-align: center; color: __TEXT_3__; font-family: __FONT_MONO__; 
    font-size: 12px; letter-spacing: 0.1em; text-transform: uppercase; 
    background: rgba(17, 24, 39, 0.4);
}

/* ── Streamlit Component Overrides ─────────────────────── */
.stTabs [data-baseweb="tab-list"] { gap: 0; background: transparent; border-bottom: 1px solid __BORDER__; }
.stTabs [data-baseweb="tab"] { 
    background: transparent; color: __TEXT_3__; padding: 12px 24px; border-radius: 0; 
    font-family: __FONT_MONO__; font-size: 11px; font-weight: 700; 
    letter-spacing: 0.12em; text-transform: uppercase; border: none; 
}
.stTabs [aria-selected="true"] { 
    background: transparent !important; color: __TEXT_1__ !important; 
    border-bottom: 2px solid __ACCENT__ !important; 
}
.stTabs [data-baseweb="tab-highlight"] { background-color: __ACCENT__ !important; }

div[data-testid="stFileUploader"] { 
    background: __BG_CARD__; border: 1px dashed __BORDER__; border-radius: 12px; padding: 20px; 
}
div[data-testid="stFileUploader"] label { color: __TEXT_2__ !important; }

*::-webkit-scrollbar { width: 8px; height: 8px; }
*::-webkit-scrollbar-track { background: __BG_PAGE__; }
*::-webkit-scrollbar-thumb { background: __BORDER__; border-radius: 4px; }
*::-webkit-scrollbar-thumb:hover { background: __BORDER_HOVER__; }

.stButton > button { 
    background: __BG_CARD__; color: __TEXT_1__; border: 1px solid __BORDER__; 
    border-radius: 8px; font-family: __FONT_MONO__; font-size: 11px; font-weight: 700; 
    letter-spacing: 0.1em; text-transform: uppercase; padding: 10px 20px; 
    transition: all 150ms ease; width: 100%;
}
.stButton > button:hover { border-color: __ACCENT__; color: __ACCENT__; background: __BG_CARD__; }
.stButton > button[kind="primary"] { background: __ACCENT__; color: __BG_PAGE__; border-color: __ACCENT__; }
.stButton > button[kind="primary"]:hover { background: __ACCENT_2__; border-color: __ACCENT_2__; color: __TEXT_1__; }

div[data-testid="stDataFrame"] { border: 1px solid __BORDER__; border-radius: 12px; overflow: hidden; }
div[data-testid="stExpander"] { 
    border: 1px solid __BORDER__; border-radius: 12px; background: __BG_CARD__; 
    margin-bottom: 12px; border-left: 3px solid __ACCENT_2__;
}
div[data-testid="stExpander"] summary { 
    font-family: __FONT_MONO__; font-size: 13px; font-weight: 600; 
    letter-spacing: 0.02em; text-transform: none; color: __TEXT_1__; 
}
.stDownloadButton > button { 
    background: transparent; border: 1px solid __ACCENT__; color: __ACCENT__; 
    font-family: __FONT_MONO__; font-size: 11px; font-weight: 700; 
    letter-spacing: 0.1em; text-transform: uppercase; border-radius: 8px; padding: 10px 20px; width: 100%;
}
div[data-baseweb="select"] > div, div[data-baseweb="select"] input { 
    background: __BG_CARD__ !important; border: 1px solid __BORDER__ !important; 
    border-radius: 8px !important; color: __TEXT_1__ !important; 
}
.stAlert { border-radius: 8px; border: 1px solid __BORDER__; }
</style>
"""
    replacements = {**DESIGN_TOKENS, **{f"RISK_{k}": v for k, v in RISK_COLORS.items()}}
    for key, value in replacements.items():
        css_template = css_template.replace(f"__{key.upper()}__", value)
    return css_template

def kpi_card(label: str, value: str | float | int, delta: str | None = None, delta_dir: str = "neutral", accent: str = "cyan") -> str:
    accent_class = ""
    if accent in ("indigo", "risk-low", "risk-medium", "risk-high", "risk-critical"): accent_class = accent
    elif accent == "risk_low": accent_class = "risk-low"
    elif accent == "risk_medium": accent_class = "risk-medium"
    elif accent == "risk_high": accent_class = "risk-high"
    elif accent == "risk_critical": accent_class = "risk-critical"
    value_str = str(value)
    delta_html = f'<div class="obs-kpi-delta {delta_dir}">{delta}</div>' if delta else ""
    return f'<div class="obs-card {accent_class}"><div class="obs-kpi-label">{label}</div><div class="obs-kpi-value">{value_str}</div>{delta_html}</div>'

def status_pill(level: Any) -> str:
    raw = getattr(level, "value", str(level))
    key = str(raw).upper()
    cls = key.lower() if key in ("LOW", "MEDIUM", "HIGH", "CRITICAL") else ""
    return f'<span class="obs-pill {cls}"><span class="dot"></span>{key}</span>'

def brand_bar() -> str:
    return '''
    <div class="obs-brand">
        <div class="obs-brand-word">
            <span class="accent">◈</span> RISK ENGINE <span class="sub">// V2.1 ENTERPRISE</span>
        </div>
        <div class="obs-micro" style="margin:0;">OBSIDIAN COMMAND UI</div>
    </div>
    '''

def ops_strip(*, env: str = "PROD", version: str = "V2.1", now: datetime | None = None) -> str:
    ts = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%d %H:%M:%S UTC")
    return f'''
    <div class="obs-ops">
        <span><span class="dot"></span>SYSTEM <b>{env}</b></span>
        <span>BUILD <b>{version}</b></span>
        <span>LAST SYNC <b>{ts}</b></span>
        <span>STATUS <b style="color: #10B981;">OPERATIONAL</b></span>
    </div>
    '''
