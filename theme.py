"""
Supply Chain Risk Engine V2 — premium B2B design system.
Electric-blue + deep slate palette, monospace command-center typography.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

DESIGN_TOKENS: dict[str, str] = {
    "bg_page": "#0F172A",
    "bg_card": "#1E293B",
    "bg_elevated": "#334155",
    "border": "#334155",
    "border_hover": "#3B82F6",
    "accent": "#3B82F6",
    "accent_2": "#8B5CF6",
    "text_1": "#F8FAFC",
    "text_2": "#94A3B8",
    "text_3": "#64748B",
    "grid": "#334155",
    "font_ui": "'JetBrains Mono', 'SF Mono', Consolas, monospace",
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
    css_template = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700;800&display=swap');

html, body, .stApp { background-color: __BG_PAGE__ !important; color: __TEXT_1__; font-family: __FONT_UI__; -webkit-font-smoothing: antialiased; }
.main .block-container { padding-top: 1.25rem !important; padding-bottom: 2rem !important; max-width: 1500px !important; }
header[data-testid="stHeader"] { background-color: __BG_PAGE__ !important; }
section[data-testid="stSidebar"] { background-color: __BG_PAGE__ !important; border-right: 1px solid __BORDER__ !important; }

h1 { font-size: 28px !important; font-weight: 700 !important; letter-spacing: -0.02em !important; color: __TEXT_1__ !important; margin: 0 0 8px !important; }
h2 { font-size: 18px !important; font-weight: 700 !important; letter-spacing: -0.01em !important; color: __TEXT_1__ !important; margin-top: 24px !important; margin-bottom: 12px !important; }
h3 { font-size: 12px !important; font-weight: 700 !important; color: __TEXT_3__ !important; text-transform: uppercase !important; letter-spacing: 0.1em !important; margin-bottom: 10px !important; }
p, span, div, label { color: __TEXT_1__; }

.obs-mono { font-family: __FONT_MONO__; font-variant-numeric: tabular-nums; }
.obs-micro { font-family: __FONT_MONO__; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.16em; color: __TEXT_3__; display: block; margin-bottom: 10px; }

.obs-brand { display: flex; align-items: baseline; justify-content: space-between; padding: 14px 0 12px; border-bottom: 1px solid __BORDER__; }
.obs-brand-word { font-family: __FONT_MONO__; font-size: 14px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: __TEXT_1__; }
.obs-brand-word .mark { color: __ACCENT__; text-shadow: 0 0 14px rgba(59, 130, 246, 0.55); }
.obs-brand-word .sub { color: __TEXT_3__; font-weight: 500; margin-left: 10px; letter-spacing: 0.08em; }

.obs-ops { display: flex; flex-wrap: wrap; gap: 22px; padding: 9px 2px; border-bottom: 1px solid __BORDER__; margin-bottom: 20px; font-family: __FONT_MONO__; font-size: 10px; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase; color: __TEXT_3__; }
.obs-ops b { color: __TEXT_2__; font-weight: 700; }
.obs-ops .dot { display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: __ACCENT__; margin-right: 7px; vertical-align: middle; box-shadow: 0 0 8px __ACCENT__; }

.obs-card { background: __BG_CARD__; border: 1px solid __BORDER__; border-radius: 8px; padding: 20px 20px 18px; margin: 6px 0; position: relative; overflow: hidden; transition: border-color 160ms ease, transform 160ms ease; }
.obs-card:hover { border-color: __BORDER_HOVER__; transform: translateY(-1px); }
.obs-card::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: __ACCENT__; }
.obs-card.indigo::before { background: __ACCENT_2__; }
.obs-card.risk-low::before { background: __RISK_LOW__; }
.obs-card.risk-medium::before { background: __RISK_MEDIUM__; }
.obs-card.risk-high::before { background: __RISK_HIGH__; }
.obs-card.risk-critical::before { background: __RISK_CRITICAL__; box-shadow: 0 0 14px rgba(239, 68, 68, 0.5); }

.obs-kpi-label { font-family: __FONT_MONO__; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.16em; color: __TEXT_3__; margin-bottom: 10px; }
.obs-kpi-value { font-family: __FONT_MONO__; font-size: 36px; font-weight: 700; color: __TEXT_1__; font-variant-numeric: tabular-nums; line-height: 1; letter-spacing: -0.02em; margin-bottom: 8px; }
.obs-kpi-delta { display: inline-block; font-family: __FONT_MONO__; font-size: 11px; font-weight: 700; padding: 3px 9px; border-radius: 6px; letter-spacing: 0.03em; }
.obs-kpi-delta.up { background: rgba(16, 185, 129, 0.14); color: __RISK_LOW__; }
.obs-kpi-delta.down { background: rgba(239, 68, 68, 0.14); color: __RISK_CRITICAL__; }
.obs-kpi-delta.neutral { background: rgba(148, 163, 184, 0.12); color: __TEXT_2__; }

.obs-pill { display: inline-flex; align-items: center; gap: 8px; font-family: __FONT_MONO__; font-size: 10px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; padding: 5px 11px; border-radius: 6px; border: 1px solid __BORDER__; color: __TEXT_2__; margin-right: 6px; }
.obs-pill .dot { width: 6px; height: 6px; border-radius: 50%; background: __TEXT_3__; }
.obs-pill.low { background: rgba(16, 185, 129, 0.1); color: __RISK_LOW__; border-color: rgba(16, 185, 129, 0.35); }
.obs-pill.low .dot { background: __RISK_LOW__; }
.obs-pill.medium { background: rgba(245, 158, 11, 0.1); color: __RISK_MEDIUM__; border-color: rgba(245, 158, 11, 0.35); }
.obs-pill.medium .dot { background: __RISK_MEDIUM__; }
.obs-pill.high { background: rgba(249, 115, 22, 0.1); color: __RISK_HIGH__; border-color: rgba(249, 115, 22, 0.35); }
.obs-pill.high .dot { background: __RISK_HIGH__; }
.obs-pill.critical { background: rgba(239, 68, 68, 0.14); color: __RISK_CRITICAL__; border-color: rgba(239, 68, 68, 0.4); }
.obs-pill.critical .dot { background: __RISK_CRITICAL__; box-shadow: 0 0 8px __RISK_CRITICAL__; }

.obs-empty { border: 1px dashed __BORDER__; border-radius: 8px; padding: 44px 24px; text-align: center; color: __TEXT_3__; font-family: __FONT_MONO__; font-size: 11px; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase; background: rgba(30, 41, 59, 0.4); }

.stTabs [data-baseweb="tab-list"] { gap: 0; background: transparent; border-bottom: 1px solid __BORDER__; }
.stTabs [data-baseweb="tab"] { background: transparent; color: __TEXT_3__; padding: 12px 22px; border-radius: 0; font-family: __FONT_MONO__; font-size: 11px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; border: none; }
.stTabs [aria-selected="true"] { background: transparent !important; color: __TEXT_1__ !important; border-bottom: 2px solid __ACCENT__ !important; }
.stTabs [data-baseweb="tab-highlight"] { background-color: __ACCENT__ !important; }

div[data-testid="stSidebar"] label { font-family: __FONT_MONO__; font-size: 10px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: __TEXT_3__; }
div[data-testid="stFileUploader"] { background: __BG_CARD__; border: 1px dashed __BORDER__; border-radius: 8px; padding: 16px; }

*::-webkit-scrollbar { width: 8px; height: 8px; }
*::-webkit-scrollbar-track { background: __BG_PAGE__; }
*::-webkit-scrollbar-thumb { background: __BORDER__; border-radius: 4px; }
*::-webkit-scrollbar-thumb:hover { background: __BORDER_HOVER__; }

.stButton > button { background: __BG_CARD__; color: __TEXT_1__; border: 1px solid __BORDER__; border-radius: 6px; font-family: __FONT_MONO__; font-size: 11px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; padding: 9px 18px; transition: all 150ms ease; }
.stButton > button:hover { border-color: __ACCENT__; color: __ACCENT__; }
.stButton > button[kind="primary"] { background: __ACCENT__; color: __TEXT_1__; border: none; }
.stButton > button[kind="primary"]:hover { filter: brightness(1.1); }

div[data-testid="stDataFrame"] { border: 1px solid __BORDER__; border-radius: 8px; overflow: hidden; }
div[data-testid="stExpander"] { border: 1px solid __BORDER__; border-radius: 8px; background: __BG_CARD__; margin-bottom: 10px; border-left: 3px solid __ACCENT__; }
div[data-testid="stExpander"] summary { font-family: __FONT_MONO__; font-size: 12px; font-weight: 600; color: __TEXT_1__; }

.stDownloadButton > button { background: transparent; border: 1px solid __ACCENT__; color: __ACCENT__; font-family: __FONT_MONO__; font-size: 11px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; border-radius: 6px; padding: 9px 18px; }
div[data-baseweb="select"] > div { background: __BG_CARD__ !important; border: 1px solid __BORDER__ !important; border-radius: 6px !important; color: __TEXT_1__ !important; }
.stAlert { border-radius: 6px; border: 1px solid __BORDER__; }
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
        '<span class="obs-brand-word"><span class="mark">◆</span> Supply Chain Risk Engine V2</span>'
        '<span class="obs-micro" style="margin:0;">Enterprise Edition</span>'
        '</div>'
    )


def ops_strip(*, env: str = "PROD", version: str = "V2", now: datetime | None = None) -> str:
    ts = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        '<div class="obs-ops">'
        f'<span><span class="dot"></span>ENV <b>{env}</b></span>'
        f'<span>BUILD <b>{version}</b></span>'
        f'<span>SYNC <b>{ts}</b></span>'
        '<span>STATUS <b style="color:#10B981;">OPERATIONAL</b></span>'
        '</div>'
    )
