"""
engine/theme.py
Theme definitions, color palettes, and visual styling tokens for the Antigravity Motion Engine.
Inspired by alchaincyf/huashu-art-motion's multi-style art grammar.
"""

from dataclasses import dataclass
from typing import Tuple

ColorRGBA = Tuple[float, float, float, float]
ColorRGB = Tuple[float, float, float]

@dataclass
class Theme:
    name: str
    bg_primary: ColorRGB
    bg_secondary: ColorRGB
    accent_primary: ColorRGBA
    accent_secondary: ColorRGBA
    text_primary: ColorRGBA
    text_secondary: ColorRGBA
    card_bg: ColorRGBA
    card_border: ColorRGBA
    glow_color: ColorRGB
    doodle_color: ColorRGBA

THEMES = {
    "cyber_neon": Theme(
        name="Cyber Neon",
        bg_primary=(0.04, 0.04, 0.06),
        bg_secondary=(0.08, 0.06, 0.14),
        accent_primary=(1.0, 0.85, 0.0, 1.0),       # Electric gold
        accent_secondary=(0.0, 0.85, 1.0, 1.0),     # Cyber cyan
        text_primary=(1.0, 1.0, 1.0, 1.0),
        text_secondary=(0.7, 0.75, 0.85, 1.0),
        card_bg=(0.08, 0.09, 0.14, 0.90),
        card_border=(0.0, 0.85, 1.0, 0.6),
        glow_color=(1.0, 0.85, 0.0),
        doodle_color=(1.0, 0.90, 0.1, 0.95),        # Hand-drawn yellow sketch
    ),
    "apple_keynote": Theme(
        name="Apple Keynote",
        bg_primary=(0.02, 0.02, 0.03),
        bg_secondary=(0.05, 0.06, 0.08),
        accent_primary=(0.2, 0.6, 1.0, 1.0),        # System blue
        accent_secondary=(0.9, 0.9, 0.95, 1.0),     # Platinum
        text_primary=(0.98, 0.98, 0.98, 1.0),
        text_secondary=(0.6, 0.65, 0.7, 1.0),
        card_bg=(0.09, 0.10, 0.13, 0.88),
        card_border=(1.0, 1.0, 1.0, 0.15),
        glow_color=(0.2, 0.6, 1.0),
        doodle_color=(0.3, 0.7, 1.0, 0.9),
    ),
    "fintech_emerald": Theme(
        name="Fintech Emerald",
        bg_primary=(0.03, 0.05, 0.04),
        bg_secondary=(0.05, 0.09, 0.07),
        accent_primary=(0.1, 0.95, 0.5, 1.0),       # High-growth emerald
        accent_secondary=(1.0, 0.8, 0.2, 1.0),      # Gold
        text_primary=(1.0, 1.0, 1.0, 1.0),
        text_secondary=(0.65, 0.8, 0.7, 1.0),
        card_bg=(0.06, 0.12, 0.09, 0.92),
        card_border=(0.1, 0.95, 0.5, 0.5),
        glow_color=(0.1, 0.95, 0.5),
        doodle_color=(0.2, 1.0, 0.6, 0.95),
    ),
    "vox_editorial": Theme(
        name="Vox Editorial",
        bg_primary=(0.08, 0.08, 0.09),
        bg_secondary=(0.12, 0.12, 0.14),
        accent_primary=(1.0, 0.25, 0.25, 1.0),      # Editorial coral red
        accent_secondary=(1.0, 0.85, 0.1, 1.0),     # Yellow
        text_primary=(1.0, 1.0, 1.0, 1.0),
        text_secondary=(0.8, 0.8, 0.85, 1.0),
        card_bg=(0.14, 0.14, 0.16, 0.95),
        card_border=(1.0, 0.25, 0.25, 0.7),
        glow_color=(1.0, 0.3, 0.3),
        doodle_color=(1.0, 0.3, 0.3, 0.95),
    )
}

def get_theme(name: str = "cyber_neon") -> Theme:
    return THEMES.get(name, THEMES["cyber_neon"])
