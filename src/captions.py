"""Arabic-aware text shaping and overlay placement for video captions.

Arabic script needs contextual shaping (letters join differently depending
on their neighbours) and right-to-left display order before it can be drawn
by ffmpeg's drawtext filter, which does neither on its own. This module wraps
arabic_reshaper + python-bidi so overlays render correctly.
"""

from __future__ import annotations

import textwrap

import arabic_reshaper
from bidi.algorithm import get_display

# Drawtext special characters that must be escaped in the text option.
_DRAWTEXT_SPECIALS = {
    "\\": "\\\\",
    ":": "\\:",
    "'": "\\'",
    "%": "\\%",
    ",": "\\,",
}


def is_arabic(text: str) -> bool:
    """Return True if the string contains Arabic letters."""
    return any("\u0600" <= ch <= "\u06ff" or "\u0750" <= ch <= "\u077f" for ch in text)


def shape(text: str) -> str:
    """Shape and reorder text for correct rendering by a non-bidi renderer."""
    if not is_arabic(text):
        return text
    return get_display(arabic_reshaper.reshape(text))


def wrap(text: str, width: int = 24) -> str:
    """Wrap a caption into lines of at most `width` characters.

    Wrapping happens before shaping so line breaks fall on word boundaries.
    Lines are joined with a literal newline for drawtext's textfile-free use.
    """
    lines = textwrap.wrap(text, width=width, break_long_words=False)
    return "\n".join(lines) if lines else text


def escape_drawtext(text: str) -> str:
    """Escape a string for use inside ffmpeg's drawtext `text` option."""
    for src, dst in _DRAWTEXT_SPECIALS.items():
        text = text.replace(src, dst)
    return text


def overlay_text(raw: str, width: int = 24) -> str:
    """Full pipeline: wrap -> shape each line -> escape for drawtext."""
    shaped_lines = [shape(line) for line in wrap(raw, width).split("\n")]
    return escape_drawtext("\n".join(shaped_lines))


def position_expr(position: str, frame_w: int, frame_h: int, box_h: int = 0) -> tuple[str, str]:
    """Return (x, y) drawtext expressions for a named overlay position.

    Supported positions: top, center, bottom. Text is horizontally centered.
    """
    x = f"(w-text_w)/2"
    margins = {"top": int(frame_h * 0.18), "center": None, "bottom": int(frame_h * 0.72)}
    if position == "center":
        y = "(h-text_h)/2"
    elif position == "bottom":
        y = str(margins["bottom"])
    else:
        y = str(margins["top"])
    return x, y
