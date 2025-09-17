"""Theme & style centralization for AEB GUI.
Provides ThemeManager with light/dark palettes and font definitions.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Palette:
    primary: str
    bg: str
    canvas_bg: str
    road: str
    text: str
    ok: str
    warn: str
    err: str
    neutral: str

LIGHT = Palette(
    primary="#0074D9",
    bg="#f0f2f5",
    canvas_bg="#e9ecef",
    road="#b0b0b0",
    text="#222",
    ok="#228B22",
    warn="#FFA500",
    err="#B22222",
    neutral="#888",
)

DARK = Palette(
    primary="#198cff",
    bg="#1e1f26",
    canvas_bg="#2a2c34",
    road="#555",
    text="#eee",
    ok="#44d060",
    warn="#ffb347",
    err="#ff6b5c",
    neutral="#777",
)

FONT_FAMILY = "Segoe UI"
FONT_TITLE = (FONT_FAMILY, 15, "bold")
FONT_SECTION = (FONT_FAMILY, 12, "bold")
FONT_LABEL = (FONT_FAMILY, 11)
FONT_LABEL_BOLD = (FONT_FAMILY, 11, "bold")
FONT_SMALL = (FONT_FAMILY, 9, "bold")
FONT_VEHICLE = (FONT_FAMILY, 10, "bold")
FONT_MONO = ("Consolas", 10)

class ThemeManager:
    def __init__(self):
        self._current = LIGHT

    @property
    def palette(self) -> Palette:
        return self._current

    def set_mode(self, mode: str):
        if mode.lower() == "dark":
            self._current = DARK
        else:
            self._current = LIGHT

    # Convenience passthroughs (optional)
    def __getattr__(self, item):  # simple delegation to palette
        return getattr(self._current, item)

THEME = ThemeManager()

# Backward-compatible color constant aliases (legacy code expected these):
COLOR_BG = THEME.bg
COLOR_PRIMARY = THEME.primary
COLOR_CANVAS_BG = THEME.canvas_bg
COLOR_ROAD = THEME.road
COLOR_TEXT = THEME.text
COLOR_OK = THEME.ok
COLOR_WARN = THEME.warn
COLOR_ERR = THEME.err
COLOR_NEUTRAL = THEME.neutral

__all__ = [
    "THEME",
    "Palette",
    "FONT_TITLE","FONT_SECTION","FONT_LABEL","FONT_LABEL_BOLD","FONT_SMALL","FONT_VEHICLE","FONT_MONO",
    # color aliases
    "COLOR_BG","COLOR_PRIMARY","COLOR_CANVAS_BG","COLOR_ROAD","COLOR_TEXT","COLOR_OK","COLOR_WARN","COLOR_ERR","COLOR_NEUTRAL",
]
