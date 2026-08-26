"""
OBSIDIAN COMMAND — enterprise B2B risk-intelligence design system.
Single source of truth for tokens; tests assert these exact values.
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
    "font_ui": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    "font_mono": "'JetBrains Mono', 'SF Mono', Consolas, monospace",
}

RISK_COLORS: dict[str, str] = {
    "LOW": "#34D399",
    "MEDIUM": "#FBBF24",
    "HIGH": "#FB923C",
    "CRITICAL": "#F87171",
}

RISK_RGB: dict[str, tuple[int, int, int]] = {
    "LOW": (52, 211, 153),
    "MEDIUM": (251, 191, 36),
    "HIGH": (251, 146, 60),
    "CRITICAL": (248, 113, 113),
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
    """Plotly layout dict. Does NOT include 'title' (each chart sets its own)."""
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
    """Full CSS block. Uses __TOKEN__ replacement (immune to f-string brace bugs)."""
    css_template = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

html, body, .stApp { background-color: __BG_PAGE__ !important; color: __TEXT_1__; font-family: __FONT_UI__; -webkit-font-smoothing: antialiased; }
.main .block-container { padding-top: 1.25rem !important; padding-bottom: 2rem !important; max-width: 1480px !important; }
header[data-testid="stHeader"] { background-color: __BG_PAGE__ !important; }
section[data-testid="stSidebar"] { background-color: __BG_PAGE__ !important; border-right: 1px solid __BORDER__ !important; }

h1 { font-size: 30px !important; font-weight: 800 !important; letter-spacing: -0.035em !important; color: __TEXT_1__ !important; margin: 0 0 4px !important; }
h2 { font-size: 19px !important; font-weight: 700 !important; letter-spacing: -0.02em !important; color: __TEXT_1__ !important; margin-top: 20px !important; }
h3 { font-size: 12px !important; font-weight: 700 !important; color: __TEXT_3__ !important; text-transform: uppercase !important; letter-spacing: 0.1em !important; margin-bottom: 10px !important; }
p, span, div, label { color: __TEXT_1__; }

.obs-mono { font-family: __FONT_MONO__; font-variant-numeric: tabular-nums; }
.obs-micro { font-family: __FONT_MONO__; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.16em; color: __TEXT_3__; display: block; margin-bottom: 10px; }

.obs-brand { display: flex; align-items: baseline; justify-content: space-between; padding: 14px 0 12px; border-bottom: 1px solid __BORDER__; }
.obs-brand-word { font-family: __FONT_MONO__; font-size: 15px; font-weight: 700; letter-spacing: 0.18em; text-transform: uppercase; color: __TEXT_1__; }
.obs-brand-word .mark { color: __ACCENT__; text-shadow: 0 0 14px rgba(34, 211, 238, 0.55); }
.obs-brand-word .sub { color: __TEXT_3__; font-weight: 500; margin-left: 10px; letter-spacing: 0.12em; }

.obs-ops { display: flex; flex-wrap: wrap; gap: 22px; padding: 9px 2px; border-bottom: 1px solid __BORDER__; margin-bottom: 20px; font-family: __FONT_MONO__; font-size: 10px; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase; color: __TEXT_3__; }
.obs-ops b { color: __TEXT_2__; font-weight: 700; }
.obs-ops .dot { display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: __ACCENT__; margin-right: 7px; vertical-align: middle; box-shadow: 0 0 8px __ACCENT__; }

.obs-card { background: linear-gradient(165deg, __BG_CARD__ 0%, #0D1526 100%); border: 1px solid __BORDER__; border-radius: 10px; padding: 20px 20px 18px; margin: 6px 0; position: relative; overflow: hidden; transition: border-color 160ms ease, transform 160ms ease; }
.obs-card:hover { border-color: __BORDER_HOVER__; transform: translateY(-1px); }
.obs-card::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: __ACCENT__; }
.obs-card.indigo::before { background: __ACCENT_2__; }
.obs-card.risk-low::before { background: __RISK_LOW__; }
.obs-card.risk-medium::before { background: __RISK_MEDIUM__; }
.obs-card.risk-high::before { background: __RISK_HIGH__; }
.obs-card.risk-critical::before { background: __RISK_CRITICAL__; box-shadow: 0 0 14px rgba(248, 113, 113, 0.5); }

.obs-kpi-label { font-family: __FONT_MONO__; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.16em; color: __TEXT_3__; margin-bottom: 10px; }
.obs-kpi-value { font-family: __FONT_MONO__; font-size: 40px; font-weight: 700; color: __TEXT_1__; font-variant-numeric: tabular-nums; line-height: 1; letter-spacing: -0.03em; margin-bottom: 8px; }
.obs-kpi-delta { display: inline-block; font-family: __FONT_MONO__; font-size: 11px; font-weight: 700; padding: 3px 9px; border-radius: 6px; letter-spacing: 0.03em; }
.obs-kpi-delta.up { background: rgba(52, 211, 153, 0.14); color: __RISK_LOW__; }
.obs-kpi-delta.down { background: rgba(248, 113, 113, 0.14); color: __RISK_CRITICAL__; }
.obs-kpi-delta.neutral { background: rgba(148, 163, 184, 0.12); color: __TEXT_2__; }

.obs-pill { display: inline-flex; align-items: center; gap: 8px; font-family: __FONT_MONO__; font-size: 10px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; padding: 5px 11px; border-radius: 6px; border: 1px solid __BORDER__; color: __TEXT_2__; margin-right: 6px; }
.obs-pill .dot { width: 6px; height: 6px; border-radius: 50%; background: __TEXT_3__; }
.obs-pill.low { background: rgba(52, 211, 153, 0.1); color: __RISK_LOW__; border-color: rgba(52, 211, 153, 0.35); }
.obs-pill.low .dot { background: __RISK_LOW__; }
.obs-pill.medium { background: rgba(251, 191, 36, 0.1); color: __RISK_MEDIUM__; border-color: rgba(251, 191, 36, 0.35); }
.obs-pill.medium .dot { background: __RISK_MEDIUM__; }
.obs-pill.high { background: rgba(251, 146, 60, 0.1); color: __RISK_HIGH__; border-color: rgba(251, 146, 60, 0.35); }
.obs-pill.high .dot { background: __RISK_HIGH__; }
.obs-pill.critical { background: rgba(248, 113, 113, 0.14); color: __RISK_CRITICAL__; border-color: rgba(248, 113, 113, 0.4); }
.obs-pill.critical .dot { background: __RISK_CRITICAL__; box-shadow: 0 0 8px __RISK_CRITICAL__; }

.obs-empty { border: 1px dashed __BORDER__; border-radius: 10px; padding: 44px 24px; text-align: center; color: __TEXT_3__; font-family: __FONT_MONO__; font-size: 11px; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase; background: rgba(17, 28, 48, 0.35); }

.stTabs [data-baseweb="tab-list"] { gap: 0; background: transparent; border-bottom: 1px solid __BORDER__; }
.stTabs [data-baseweb="tab"] { background: transparent; color: __TEXT_3__; padding: 12px 22px; border-radius: 0; font-family: __FONT_MONO__; font-size: 11px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; border: none; }
.stTabs [aria-selected="true"] { background: transparent !important; color: __TEXT_1__ !important; border-bottom: 2px solid __ACCENT__ !important; }
.stTabs [data-baseweb="tab-highlight"] { background-color: __ACCENT__ !important; }

div[data-testid="stSidebar"] label { font-family: __FONT_MONO__; font-size: 10px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: __TEXT_3__; }
div[data-testid="stFileUploader"] { background: __BG_CARD__; border: 1px dashed __BORDER__; border-radius: 10px; padding: 16px; }

*::-webkit-scrollbar { width: 8px; height: 8px; }
*::-webkit-scrollbar-track { background: __BG_PAGE__; }
*::-webkit-scrollbar-thumb { background: __BORDER__; border-radius: 4px; }
*::-webkit-scrollbar-thumb:hover { background: __BORDER_HOVER__; }

.stButton > button { background: __BG_CARD__; color: __TEXT_1__; border: 1px solid __BORDER__; border-radius: 8px; font-family: __FONT_MONO__; font-size: 11px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; padding: 9px 18px; transition: all 150ms ease; }
.stButton > button:hover { border-color: __ACCENT__; color: __ACCENT__; }
.stButton > button[kind="primary"] { background: linear-gradient(135deg, __ACCENT__ 0%, __ACCENT_2__ 130%); color: __BG_PAGE__; border: none; }
.stButton > button[kind="primary"]:hover { color: __BG_PAGE__; filter: brightness(1.12); }

div[data-testid="stDataFrame"] { border: 1px solid __BORDER__; border-radius: 10px; overflow: hidden; }
div[data-testid="stExpander"] { border: 1px solid __BORDER__; border-radius: 10px; background: __BG_CARD__; margin-bottom: 10px; border-left: 3px solid __ACCENT_2__; }
div[data-testid="stExpander"] summary { font-family: __FONT_MONO__; font-size: 12px; font-weight: 600; color: __TEXT_1__; }

.stDownloadButton > button { background: transparent; border: 1px solid __ACCENT__; color: __ACCENT__; font-family: __FONT_MONO__; font-size: 11px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; border-radius: 8px; padding: 9px 18px; }
div[data-baseweb="select"] > div { background: __BG_CARD__ !important; border: 1px solid __BORDER__ !important; border-radius: 8px !important; color: __TEXT_1__ !important; }
.stAlert { border-radius: 8px; border: 1px solid __BORDER__; }
</style>
"""
    replacements = {**DESIGN_TOKENS, **{f"RISK_{k}": v for k, v in RISK_COLORS.items()}}
    for key, value in replacements.items():
        css_template = css_template.replace(f"__{key.upper()}__", value)
    return css_template


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


def brand_bar() -> str:
    return (
        '<div class="obs-brand">'
        '<span class="obs-brand-word"><span class="mark">◈</span> Risk Engine <span class="sub">// V2.1 · SUPPLY CHAIN RISK INTELLIGENCE</span></span>'
        '<span class="obs-micro" style="margin:0;">Obsidian Command</span>'
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
