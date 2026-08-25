"""
OBSIDIAN COMMAND — enterprise B2B risk-intelligence design system.

PUBLIC API (stable, headless-importable):
    DESIGN_TOKENS           # full token registry
    RISK_COLORS             # semantic risk palette (separate from brand)
    get_plotly_layout()     # Plotly layout dict for any figure in the app
    inject_theme_css()      # full CSS string with Google Fonts import
    kpi_card(label, value, delta=None, accent='cyan')
    status_pill(level)      # RiskLevel enum value or string
    brand_bar()             # 2px gradient + mono wordmark
    ops_strip()             # ENV · VERSION · timestamp mono strip
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
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
    """Plotly layout dict enforcing OBSIDIAN COMMAND tokens."""
    return {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {
            "family": DESIGN_TOKENS["font_ui"],
            "color": DESIGN_TOKENS["text_1"],
        },
        "title": {"font": {"color": DESIGN_TOKENS["text_1"], "size": 14}},
        "xaxis": {
            "gridcolor": DESIGN_TOKENS["grid"],
            "zerolinecolor": DESIGN_TOKENS["grid"],
            "color": DESIGN_TOKENS["text_2"],
            "linecolor": DESIGN_TOKENS["grid"],
        },
        "yaxis": {
            "gridcolor": DESIGN_TOKENS["grid"],
            "zerolinecolor": DESIGN_TOKENS["grid"],
            "color": DESIGN_TOKENS["text_2"],
            "linecolor": DESIGN_TOKENS["grid"],
        },
        "margin": {"l": 0, "r": 0, "t": 32, "b": 32},
        "legend": {
            "bgcolor": "rgba(0,0,0,0)",
            "font": {"color": DESIGN_TOKENS["text_2"]},
        },
        "colorway": [
            DESIGN_TOKENS["accent"],
            DESIGN_TOKENS["accent_2"],
            RISK_COLORS["HIGH"],
            RISK_COLORS["MEDIUM"],
            RISK_COLORS["LOW"],
        ],
    }


def inject_theme_css() -> str:
    """Full CSS block injected via st.markdown(unsafe_allow_html=True)."""
    tokens = DESIGN_TOKENS
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, .stApp {{
    background-color: {tokens['bg_page']} !important;
    color: {tokens['text_1']};
    font-family: {tokens['font_ui']};
    font-feature-settings: "ss01", "cv11";
}}

/* ── Typography ────────────────────────────────────────── */
h1, h2, h3, h4 {{
    color: {tokens['text_1']};
    font-weight: 600;
    letter-spacing: -0.01em;
    margin-top: 0;
}}
h1 {{ font-size: 28px; }}
h2 {{ font-size: 20px; }}
h3 {{ font-size: 15px; color: {tokens['text_2']}; text-transform: uppercase; letter-spacing: 0.08em; }}
p, span, div, label {{ color: {tokens['text_1']}; }}

.obs-mono {{
    font-family: {tokens['font_mono']};
    font-variant-numeric: tabular-nums;
    letter-spacing: 0;
}}

.obs-micro {{
    font-family: {tokens['font_mono']};
    font-size: 11px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: {tokens['text_3']};
}}

/* ── Brand bar ─────────────────────────────────────────── */
.obs-brand {{
    position: relative;
    padding: 14px 20px 10px;
    margin-bottom: 2px;
}}
.obs-brand::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, {tokens['accent']} 0%, {tokens['accent_2']} 60%, transparent 100%);
}}
.obs-brand-word {{
    font-family: {tokens['font_mono']};
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.22em;
    color: {tokens['text_1']};
    text-transform: uppercase;
}}
.obs-brand-word span {{
    color: {tokens['text_3']};
    font-weight: 400;
}}

/* ── Ops strip ─────────────────────────────────────────── */
.obs-ops {{
    display: flex;
    gap: 18px;
    padding: 8px 20px;
    border-top: 1px solid {tokens['border']};
    border-bottom: 1px solid {tokens['border']};
    margin-bottom: 18px;
    font-family: {tokens['font_mono']};
    font-size: 11px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: {tokens['text_3']};
}}
.obs-ops b {{ color: {tokens['text_2']}; font-weight: 600; }}
.obs-ops .dot {{
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: {tokens['accent']};
    margin-right: 6px;
    vertical-align: middle;
    box-shadow: 0 0 6px {tokens['accent']};
}}

/* ── Cards ─────────────────────────────────────────────── */
.obs-card {{
    background: {tokens['bg_card']};
    border: 1px solid {tokens['border']};
    border-left: 3px solid {tokens['accent']};
    border-radius: 12px;
    padding: 16px 18px;
    margin: 8px 0;
    transition: border-color 150ms ease;
}}
.obs-card:hover {{ border-color: {tokens['border_hover']}; }}
.obs-card.indigo {{ border-left-color: {tokens['accent_2']}; }}
.obs-card.risk-low {{ border-left-color: {RISK_COLORS['LOW']}; }}
.obs-card.risk-medium {{ border-left-color: {RISK_COLORS['MEDIUM']}; }}
.obs-card.risk-high {{ border-left-color: {RISK_COLORS['HIGH']}; }}
.obs-card.risk-critical {{ border-left-color: {RISK_COLORS['CRITICAL']}; }}

.obs-kpi-label {{
    font-family: {tokens['font_mono']};
    font-size: 11px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: {tokens['text_3']};
    margin-bottom: 8px;
}}
.obs-kpi-value {{
    font-family: {tokens['font_mono']};
    font-size: 32px;
    font-weight: 600;
    color: {tokens['text_1']};
    font-variant-numeric: tabular-nums;
    line-height: 1;
    margin-bottom: 6px;
}}
.obs-kpi-delta {{
    display: inline-block;
    font-family: {tokens['font_mono']};
    font-size: 11px;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 999px;
    letter-spacing: 0.04em;
}}
.obs-kpi-delta.up {{ background: rgba(52, 211, 153, 0.12); color: {RISK_COLORS['LOW']}; }}
.obs-kpi-delta.down {{ background: rgba(248, 113, 113, 0.12); color: {RISK_COLORS['CRITICAL']}; }}
.obs-kpi-delta.neutral {{ background: rgba(148, 163, 184, 0.12); color: {tokens['text_2']}; }}

/* ── Pills ─────────────────────────────────────────────── */
.obs-pill {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-family: {tokens['font_mono']};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 999px;
    border: 1px solid {tokens['border']};
    color: {tokens['text_2']};
}}
.obs-pill .dot {{
    width: 6px; height: 6px; border-radius: 50%;
    background: {tokens['text_3']};
}}
.obs-pill.low {{ background: rgba(52, 211, 153, 0.1); color: {RISK_COLORS['LOW']}; border-color: rgba(52, 211, 153, 0.3); }}
.obs-pill.low .dot {{ background: {RISK_COLORS['LOW']}; }}
.obs-pill.medium {{ background: rgba(251, 191, 36, 0.1); color: {RISK_COLORS['MEDIUM']}; border-color: rgba(251, 191, 36, 0.3); }}
.obs-pill.medium .dot {{ background: {RISK_COLORS['MEDIUM']}; }}
.obs-pill.high {{ background: rgba(251, 146, 60, 0.1); color: {RISK_COLORS['HIGH']}; border-color: rgba(251, 146, 60, 0.3); }}
.obs-pill.high .dot {{ background: {RISK_COLORS['HIGH']}; }}
.obs-pill.critical {{ background: rgba(248, 113, 113, 0.12); color: {RISK_COLORS['CRITICAL']}; border-color: rgba(248, 113, 113, 0.3); }}
.obs-pill.critical .dot {{ background: {RISK_COLORS['CRITICAL']}; box-shadow: 0 0 6px {RISK_COLORS['CRITICAL']}; }}

/* ── Empty state ───────────────────────────────────────── */
.obs-empty {{
    border: 1px dashed {tokens['border']};
    border-radius: 12px;
    padding: 28px 24px;
    text-align: center;
    color: {tokens['text_3']};
    font-family: {tokens['font_mono']};
    font-size: 12px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}}

/* ── Streamlit overrides ───────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    gap: 2px;
    background: transparent;
    border-bottom: 1px solid {tokens['border']};
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent;
    color: {tokens['text_2']};
    padding: 10px 18px;
    border-radius: 0;
    font-family: {tokens['font_mono']};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    border: none;
}}
.stTabs [aria-selected="true"] {{
    background: transparent !important;
    color: {tokens['accent']} !important;
    border-bottom: 2px solid {tokens['accent']} !important;
}}
.stTabs [data-baseweb="tab-highlight"] {{
    background-color: {tokens['accent']} !important;
}}

div[data-testid="stSidebar"] {{
    background: {tokens['bg_page']};
    border-right: 1px solid {tokens['border']};
}}
div[data-testid="stSidebar"] label {{
    font-family: {tokens['font_mono']};
    font-size: 11px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: {tokens['text_3']};
}}

div[data-testid="stFileUploader"] {{
    background: {tokens['bg_card']};
    border: 1px dashed {tokens['border']};
    border-radius: 12px;
    padding: 14px;
}}

/* Scrollbars */
*::-webkit-scrollbar {{ width: 8px; height: 8px; }}
*::-webkit-scrollbar-track {{ background: {tokens['bg_page']}; }}
*::-webkit-scrollbar-thumb {{
    background: {tokens['border']};
    border-radius: 4px;
}}
*::-webkit-scrollbar-thumb:hover {{ background: {tokens['border_hover']}; }}

/* Buttons */
.stButton > button {{
    background: {tokens['bg_card']};
    color: {tokens['text_1']};
    border: 1px solid {tokens['border']};
    border-radius: 8px;
    font-family: {tokens['font_mono']};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 8px 16px;
    transition: all 150ms ease;
}}
.stButton > button:hover {{
    border-color: {tokens['accent']};
    color: {tokens['accent']};
    background: {tokens['bg_card']};
}}
.stButton > button[kind="primary"] {{
    background: {tokens['accent']};
    color: {tokens['bg_page']};
    border-color: {tokens['accent']};
}}
.stButton > button[kind="primary"]:hover {{
    background: {tokens['accent_2']};
    border-color: {tokens['accent_2']};
    color: {tokens['text_1']};
}}

/* Metrics (fallback when not using obs-card) */
div[data-testid="stMetric"] {{
    background: {tokens['bg_card']};
    border: 1px solid {tokens['border']};
    border-left: 3px solid {tokens['accent']};
    border-radius: 12px;
    padding: 14px 16px;
}}
div[data-testid="stMetric"] label {{
    font-family: {tokens['font_mono']};
    font-size: 11px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: {tokens['text_3']};
}}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
    font-family: {tokens['font_mono']};
    font-variant-numeric: tabular-nums;
    color: {tokens['text_1']};
}}

/* Tables */
div[data-testid="stDataFrame"] {{
    border: 1px solid {tokens['border']};
    border-radius: 12px;
    overflow: hidden;
}}

/* Expander (for narratives) */
div[data-testid="stExpander"] {{
    border: 1px solid {tokens['border']};
    border-radius: 12px;
    background: {tokens['bg_card']};
    margin-bottom: 8px;
}}
div[data-testid="stExpander"] summary {{
    font-family: {tokens['font_mono']};
    font-size: 12px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: {tokens['text_1']};
}}

/* Sidebar */
.css-1d39hrn, section[data-testid="stSidebar"] {{
    background: {tokens['bg_page']};
}}

/* Download buttons */
.stDownloadButton > button {{
    background: transparent;
    border: 1px solid {tokens['accent']};
    color: {tokens['accent']};
    font-family: {tokens['font_mono']};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    border-radius: 8px;
    padding: 8px 16px;
}}

/* Selectbox / multiselect */
div[data-baseweb="select"] > div {{
    background: {tokens['bg_card']};
    border: 1px solid {tokens['border']};
    border-radius: 8px;
    color: {tokens['text_1']};
}}

/* Remove any legacy neon green */
.stAlert {{ border-radius: 8px; }}
</style>
"""


def kpi_card(
    label: str,
    value: str | float | int,
    delta: str | None = None,
    delta_dir: str = "neutral",
    accent: str = "cyan",
) -> str:
    """Render a KPI card. accent in {cyan, indigo, risk-low, risk-medium, risk-high, risk-critical}."""
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

    value_str = str(value)
    delta_html = ""
    if delta is not None:
        dir_cls = delta_dir if delta_dir in ("up", "down", "neutral") else "neutral"
        delta_html = f'<div class="obs-kpi-delta {dir_cls}">{delta}</div>'

    return (
        f'<div class="obs-card {accent_class}">'
        f'<div class="obs-kpi-label">{label}</div>'
        f'<div class="obs-kpi-value">{value_str}</div>'
        f'{delta_html}'
        f'</div>'
    )


def status_pill(level: Any) -> str:
    """Render a risk status pill. Accepts RiskLevel enum or string."""
    raw = getattr(level, "value", str(level))
    key = str(raw).upper()
    cls = key.lower() if key in ("LOW", "MEDIUM", "HIGH", "CRITICAL") else ""
    return f'<span class="obs-pill {cls}"><span class="dot"></span>{key}</span>'


def brand_bar() -> str:
    """Gradient brand bar with mono wordmark."""
    return (
        '<div class="obs-brand">'
        '<span class="obs-brand-word">Risk Engine <span>//</span> V2.1 <span>· Obsidian Command</span></span>'
        '</div>'
    )


def ops_strip(
    *,
    env: str = "PROD",
    version: str = "V2.1",
    now: datetime | None = None,
) -> str:
    """Mono ops strip: ENV · VERSION · timestamp."""
    ts = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        f'<div class="obs-ops">'
        f'<span><span class="dot"></span><b>{env}</b></span>'
        f'<span>ENGINE <b>{version}</b></span>'
        f'<span>REFRESH <b>{ts}</b></span>'
        f'<span>MODE <b>LIVE</b></span>'
        f'</div>'
    )
