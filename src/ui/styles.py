"""
src/ui/styles.py — Optimized Glassmorphic Dark Design CSS.
"""
from __future__ import annotations

import theme


def get_custom_css() -> str:
    """Return non-laggy, optimized glassmorphic CSS rules."""
    return theme.inject_theme_css() + """
<style>
/* Additional Glassmorphic Cyberpunk Accents */
.recruiter-demo-btn {
    background: linear-gradient(135deg, #00E5FF 0%, #7C3AED 100%) !important;
    color: #FFFFFF !important;
    font-weight: 800 !important;
    letter-spacing: 0.05em !important;
    border-radius: 12px !important;
    box-shadow: 0 0 20px rgba(0, 229, 255, 0.4) !important;
}

.auth-card {
    max-width: 460px;
    margin: 80px auto;
    background: rgba(11, 15, 25, 0.85);
    backdrop-filter: blur(24px);
    border: 1px solid rgba(0, 229, 255, 0.25);
    border-radius: 20px;
    padding: 40px;
    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.7);
}
</style>
"""
