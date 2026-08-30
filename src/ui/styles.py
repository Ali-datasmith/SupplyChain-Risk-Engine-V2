"""
src/ui/styles.py — Optimized Glassmorphic Dark Design CSS.
"""
from __future__ import annotations

import theme


def get_custom_css() -> str:
    """Return non-laggy, optimized glassmorphic CSS rules."""
    return theme.inject_theme_css() + """
<style>
/* Additional Glassmorphic Cyberpunk Accents & Glowing Login Box */
.recruiter-demo-btn {
    background: linear-gradient(135deg, #00E5FF 0%, #7C3AED 100%) !important;
    color: #FFFFFF !important;
    font-weight: 800 !important;
    letter-spacing: 0.05em !important;
    border-radius: 12px !important;
    box-shadow: 0 0 20px rgba(0, 229, 255, 0.4) !important;
}

.auth-card {
    max-width: 480px;
    margin: 40px auto 30px auto;
    background: linear-gradient(160deg, rgba(11, 18, 32, 0.95), rgba(4, 6, 12, 0.98));
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid #00E5FF;
    border-radius: 20px;
    padding: 36px 32px;
    box-shadow: 0 0 35px rgba(0, 229, 255, 0.35), 0 0 15px rgba(0, 229, 255, 0.2), inset 0 0 20px rgba(0, 229, 255, 0.1);
    position: relative;
    transition: all 0.3s ease-in-out;
}

.auth-card:hover {
    box-shadow: 0 0 50px rgba(0, 229, 255, 0.55), 0 0 25px rgba(0, 229, 255, 0.3), inset 0 0 30px rgba(0, 229, 255, 0.15);
    border-color: #7DF3FF;
}

.auth-card h2 {
    color: #00E5FF !important;
    text-shadow: 0 0 15px rgba(0, 229, 255, 0.7), 0 0 30px rgba(0, 229, 255, 0.4);
    font-weight: 800 !important;
    letter-spacing: -0.02em !important;
    margin-bottom: 12px !important;
    border-bottom: none !important;
}

.auth-card hr {
    border-color: rgba(0, 229, 255, 0.25) !important;
    margin: 18px 0 !important;
}
</style>
"""
