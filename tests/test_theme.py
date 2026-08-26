"""Theme tests — match current palette."""
from __future__ import annotations

import re

import pytest

import theme


def test_design_tokens_exact_hexes() -> None:
    expected = {
        "bg_page": "#0F172A",
        "bg_card": "#1E293B",
        "border": "#334155",
        "accent": "#3B82F6",
        "accent_2": "#8B5CF6",
        "text_1": "#F8FAFC",
        "text_2": "#94A3B8",
        "text_3": "#64748B",
    }
    for key, value in expected.items():
        assert theme.DESIGN_TOKENS[key] == value


def test_risk_colors_exact_hexes() -> None:
    expected = {
        "LOW": "#10B981",
        "MEDIUM": "#F59E0B",
        "HIGH": "#F97316",
        "CRITICAL": "#EF4444",
    }
    assert theme.RISK_COLORS == expected


def test_plotly_layout_required_keys_and_colors() -> None:
    layout = theme.get_plotly_layout()
    assert layout["paper_bgcolor"] == "rgba(0,0,0,0)"
    assert layout["plot_bgcolor"] == "rgba(0,0,0,0)"
    assert layout["font"]["color"] == theme.DESIGN_TOKENS["text_1"]
    assert layout["xaxis"]["gridcolor"] == theme.DESIGN_TOKENS["grid"]
    assert layout["yaxis"]["gridcolor"] == theme.DESIGN_TOKENS["grid"]
    assert "colorway" in layout


def test_inject_theme_css_google_fonts() -> None:
    css = theme.inject_theme_css()
    assert "fonts.googleapis.com" in css
    assert "JetBrains+Mono" in css or "JetBrains Mono" in css


def test_inject_theme_css_no_forbidden_hex() -> None:
    css = theme.inject_theme_css()
    forbidden = {"#00FF41", "#00ff41", "#FF4B4B", "#ff4b4b"}
    css_upper = css.upper()
    for color in forbidden:
        assert color.upper() not in css_upper


def test_inject_theme_css_required_classes() -> None:
    css = theme.inject_theme_css()
    for required in (".obs-card", ".obs-pill", ".obs-micro", ".obs-brand", ".obs-ops", ".obs-empty"):
        assert required in css


def test_kpi_card_returns_css_classes() -> None:
    html = theme.kpi_card("Test", "42", delta="+5%", delta_dir="up", accent="cyan")
    assert "obs-card" in html
    assert "obs-kpi-label" in html
    assert "obs-kpi-value" in html
    assert "Test" in html
    assert "42" in html


def test_status_pill_returns_css_class_for_risk_level() -> None:
    html_low = theme.status_pill("LOW")
    html_crit = theme.status_pill("CRITICAL")
    assert "obs-pill" in html_low
    assert "low" in html_low
    assert "critical" in html_crit

    from schemas.narrative_schema import RiskLevel
    html_enum = theme.status_pill(RiskLevel.HIGH)
    assert "high" in html_enum
    assert "obs-pill" in html_enum


def test_brand_bar_contains_wordmark() -> None:
    html = theme.brand_bar()
    assert "obs-brand" in html
    assert "SUPPLY CHAIN RISK ENGINE" in html.upper() or "Supply Chain Risk Engine" in html


def test_ops_strip_contains_env_version_timestamp() -> None:
    html = theme.ops_strip()
    assert "obs-ops" in html
    assert "PROD" in html
    assert "V2" in html
    assert re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", html)
