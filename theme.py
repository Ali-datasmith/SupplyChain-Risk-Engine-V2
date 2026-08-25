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
    """
    Plotly layout dict enforcing OBSIDIAN COMMAND tokens.
    NOTE: Does NOT include 'title' — each chart sets its own title text.
    """
    return {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {
            "family": DESIGN_TOKENS["font_ui"],
            "color": DESIGN_TOKENS["text_1"],
        },
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
    border-top: 1px solid {
