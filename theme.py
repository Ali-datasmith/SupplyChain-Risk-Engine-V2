"""
OBSIDIAN COMMAND — enterprise B2B risk-intelligence design system.
Uses __TOKEN__ replacement to completely bypass f-string brace-escaping issues.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

DESIGN_TOKENS: dict[str, str] = {
    "bg_page": "#0B1220",
    "bg_card": "#111C30",
    "bg_elevated": "#16233A",
    "border": "#1E2A44",
    "border_hover": "#22D3EE",
    "accent": "#22D3EE",
    "accent_2": "#818CF8",
    "text_1": "#E6EDF6",
    "text_2": "#94A3B8",
    "text_3": "#64748B",
    "grid": "#16233A",
    "font_ui": "'Inter', sans-serif",
    "font_mono": "'JetBrains Mono', 'SF Mono', Consolas, monospace",
}

RISK_COLORS: dict[str, str] = {
    "LOW": "#34D399",
    "MEDIUM": "#FBBF24",
    "HIGH": "#FB923C",
    "CRITICAL": "#F87171",
}

def get_plotly_layout() -> dict[str, Any]:
    """Plotly layout dict. NOTE: Does NOT include 'title' or trace-level properties."""
    return {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": DESIGN_TOKENS["font_ui"], "color": DESIGN_TOKENS["text_1"], "size": 12},
        "xaxis": {"gridcolor": DESIGN_TOKENS["grid"], "zerolinecolor": DESIGN_TOKENS["grid"], "color": DESIGN_TOKENS["text_2"], "linecolor": DESIGN_TOKENS["grid"]},
        "yaxis": {"gridcolor": DESIGN_TOKENS["grid"], "zerolinecolor": DESIGN_TOKENS["grid"], "color": DESIGN_TOKENS["text_2"], "linecolor": DESIGN_TOKENS["grid"]},
        "margin": {"l": 0, "r": 0, "t": 40, "b": 32},
        "legend": {"bgcolor": "rgba(0,0,0,0)", "font": {"color": DESIGN_TOKENS["text_2"]}},
        "colorway": [DESIGN_TOKENS["accent"], DESIGN_TOKENS["accent_2"], RISK_COLORS["HIGH"], RISK_COLORS["MEDIUM"], RISK_COLORS["LOW"]],
    }

def inject_theme_css() -> str:
    css_template = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
html, body, .stApp { background-color: __BG_PAGE__ !important; color: __TEXT_1__; font-family: __FONT_UI__; }
h1, h2, h3, h4 { color: __TEXT_1__; font-weight: 600; letter-spacing: -0.01em; margin-top: 0; }
h1 { font-size: 28px; } h2 { font-size: 20px; }
h3 { font-size: 14px; color: __TEXT_2__; text-transform: uppercase; letter-spacing: 0.08em; }
.obs-mono { font-family: __FONT_MONO__; font-variant-numeric: tabular-nums; }
.obs-micro { font-family: __FONT_MONO__; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.12em; color: __TEXT_3__; margin-bottom: 8px; }
.obs-brand { position: relative; padding: 14px 20px 10px; margin-bottom: 2px; }
.obs-brand::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, __ACCENT__ 0%, __ACCENT_2__ 60%, transparent 100%); }
.obs-brand-word { font-family: __FONT_MONO__; font-size: 13px; font-weight: 600; letter-spacing: 0.22em; color: __TEXT_1__; text-transform: uppercase; }
.obs-brand-word span { color: __TEXT_3__; font-weight: 400; }
.obs-ops { display: flex; gap: 18px; padding: 8px 20px; border-top: 1px solid __BORDER__; border-bottom: 1px solid __BORDER__; margin-bottom: 18px; font-family: __FONT_MONO__; font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: __TEXT_3__; }
.obs-ops b { color: __TEXT_2__; font-weight: 600; }
.obs-ops .dot { display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: __ACCENT__; margin-right: 6px; vertical-align: middle; box-shadow: 0 0 6px __ACCENT__; }
.obs-card { background: __BG_CARD__; border: 1px solid __BORDER__; border-left: 3px solid __ACCENT__; border-radius: 8px; padding: 16px 18px; margin: 8px 0; transition: border-color 150ms ease; }
.obs-card:hover { border-color: __BORDER_HOVER__; }
.obs-card.indigo { border-left-color: __ACCENT_2__; }
.obs-card.risk-low { border-left-color: __RISK_LOW__; }
.obs-card.risk-medium { border-left-color: __RISK_MEDIUM__; }
.obs-card.risk-high { border-left-color: __RISK_HIGH__; }
.obs-card.risk-critical { border-left-color: __RISK_CRITICAL__; }
.obs-kpi-label { font-family: __FONT_MONO__; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.12em; color: __TEXT_3__; margin-bottom: 8px; }
.obs-kpi-value { font-family: __FONT_MONO__; font-size: 32px; font-weight: 600; color: __TEXT_1__; font-variant-numeric: tabular-nums; line-height: 1; margin-bottom: 6px; }
.obs-kpi-delta { display: inline-block; font-family: __FONT_MONO__; font-size: 11px; font-weight: 600; padding: 3px 8px; border-radius: 999px; letter-spacing: 0.04em; }
.obs-kpi-delta.up { background: rgba(52, 211, 153, 0.12); color: __RISK_LOW__; }
.obs-kpi-delta.down { background: rgba(248, 113, 113, 0.12); color: __RISK_CRITICAL__; }
.obs-kpi-delta.neutral { background: rgba(148, 163, 184, 0.12); color: __TEXT_2__; }
.obs-pill { display: inline-flex; align-items: center; gap: 8px; font-family: __FONT_MONO__; font-size: 11px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; padding: 4px 10px; border-radius: 999px; border: 1px solid __BORDER__; color: __TEXT_2__; }
.obs-pill .dot { width: 6px; height: 6px; border-radius: 50%; background: __TEXT_3__; }
.obs-pill.low { background: rgba(52, 211, 153, 0.1); color: __RISK_LOW__; border-color: rgba(52, 211, 153, 0.3); }
.obs-pill.low .dot { background: __RISK_LOW__; }
.obs-pill.medium { background: rgba(251, 191, 36, 0.1); color: __RISK_MEDIUM__; border-color: rgba(251, 191, 36, 0.3); }
.obs-pill.medium .dot { background: __RISK_MEDIUM__; }
.obs-pill.high { background: rgba(251, 146, 60, 0.1); color: __RISK_HIGH__; border-color: rgba(251, 146, 60, 0.3); }
.obs-pill.high .dot { background: __RISK_HIGH__; }
.obs-pill.critical { background: rgba(248, 113, 113, 0.12); color: __RISK_CRITICAL__; border-color: rgba(248, 113, 113, 0.3); }
.obs-pill.critical .dot { background: __RISK_CRITICAL__; box-shadow: 0 0 6px __RISK_CRITICAL__; }
.obs-empty { border: 1px dashed __BORDER__; border-radius: 8px; padding: 28px 24px; text-align: center; color: __TEXT_3__; font-family: __FONT_MONO__; font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; }
.stTabs [data-baseweb="tab-list"] { gap: 2px; background: transparent; border-bottom: 1px solid __BORDER__; }
.stTabs [data-baseweb="tab"] { background: transparent; color: __TEXT_2__; padding: 10px 18px; border-radius: 0; font-family: __FONT_MONO__; font-size: 11px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; border: none; }
.stTabs [aria-selected="true"] { background: transparent !important; color: __ACCENT__ !important; border-bottom: 2px solid __ACCENT__ !important; }
div[data-testid="stSidebar"] { background: __BG_PAGE__; border-right: 1px solid __BORDER__; }
div[data-testid="stSidebar"] label { font-family: __FONT_MONO__; font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: __TEXT_3__; }
div[data-testid="stFileUploader"] { background: __BG_CARD__; border: 1px dashed __BORDER__; border-radius: 8px; padding: 14px; }
*::-webkit-scrollbar { width: 8px; height: 8px; }
*::-webkit-scrollbar-track { background: __BG_PAGE__; }
*::-webkit-scrollbar-thumb { background: __BORDER__; border-radius: 4px; }
.stButton > button { background: __BG_CARD__; color: __TEXT_1__; border: 1px solid __BORDER__; border-radius: 6px; font-family: __FONT_MONO__; font-size: 11px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; padding: 8px 16px; transition: all 150ms ease; }
.stButton > button:hover { border-color: __ACCENT__; color: __ACCENT__; }
.stButton > button[kind="primary"] { background: __ACCENT__; color: __BG_PAGE__; border-color: __ACCENT__; }
.stButton > button[kind="primary"]:hover { background: __ACCENT_2__; border-color: __ACCENT_2__; color: __TEXT_1__; }
div[data-testid="stMetric"] { background: __BG_CARD__; border: 1px solid __BORDER__; border-left: 3px solid __ACCENT__; border-radius: 8px; padding: 14px 16px; }
div[data-testid="stMetric"] label { font-family: __FONT_MONO__; font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase; color: __TEXT_3__; }
div[data-testid="stMetric"] div[data-testid="stMetricValue"] { font-family: __FONT_MONO__; font-variant-numeric: tabular-nums; color: __TEXT_1__; }
div[data-testid="stDataFrame"] { border: 1px solid __BORDER__; border-radius: 8px; overflow: hidden; }
div[data-testid="stExpander"] { border: 1px solid __BORDER__; border-radius: 8px; background: __BG_CARD__; margin-bottom: 8px; }
div[data-testid="stExpander"] summary { font-family: __FONT_MONO__; font-size: 12px; letter-spacing: 0.06em; text-transform: uppercase; color: __TEXT_1__; }
.stDownloadButton > button { background: transparent; border: 1px solid __ACCENT__; color: __ACCENT__; font-family: __FONT_MONO__; font-size: 11px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; border-radius: 6px; padding: 8px 16px; }
div[data-baseweb="select"] > div { background: __BG_CARD__; border: 1px solid __BORDER__; border-radius: 6px; color: __TEXT_1__; }
.stAlert { border-radius: 8px; }
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
    return '<div class="obs-brand"><span class="obs-brand-word">Risk Engine <span>//</span> V2.1 <span>· Obsidian Command</span></span></div>'

def ops_strip(*, env: str = "PROD", version: str = "V2.1", now: datetime | None = None) -> str:
    ts = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f'<div class="obs-ops"><span><span class="dot"></span><b>{env}</b></span><span>ENGINE <b>{version}</b></span><span>REFRESH <b>{ts}</b></span><span>MODE <b>LIVE</b></span></div>'
