"""Primitives: tokens, outlined type, SVG documents, and the weekly now strip."""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from functools import lru_cache
from pathlib import Path
from typing import Final

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.ttFont import TTFont as TTFontType
from fontTools.varLib.instancer import instantiateVariableFont

ROOT: Final[Path] = Path(__file__).resolve().parent.parent
FONTS: Final[Path] = ROOT / "assets" / "fonts"
TOKENS_PATH: Final[Path] = ROOT / "assets" / "src" / "tokens.json"
DIST: Final[Path] = ROOT / "assets" / "dist"

Theme = dict[str, str]

# The five hues cycle through tokens, spans, and bars so every module reads
# as one system.
HUES: Final[tuple[str, ...]] = ("T1", "T2", "T3", "T4", "T5")


def load_tokens() -> dict[str, Theme]:
    """Read the light and dark palettes."""
    raw = json.loads(TOKENS_PATH.read_text(encoding="utf-8"))
    return {"light": raw["light"], "dark": raw["dark"]}


@lru_cache(maxsize=8)
def _load_font(path: str, opsz: float, wght: float) -> TTFontType:
    """Open a TTF and pin variable axes when the font has them."""
    font = TTFont(path)
    if "fvar" in font:
        font = instantiateVariableFont(
            font,
            {"opsz": opsz, "wght": wght},
            inplace=False,
        )
    return font


def newsreader(*, italic: bool) -> TTFontType:
    """Display serif at optical size 72, weight 400."""
    name = "Newsreader-Italic.ttf" if italic else "Newsreader-Regular.ttf"
    return _load_font(str(FONTS / name), 72.0, 400.0)


def plex_mono() -> TTFontType:
    """Instrument labels. Static Regular file, axes ignored."""
    return _load_font(str(FONTS / "IBMPlexMono-Regular.ttf"), 12.0, 400.0)


def outline_text(
    font: TTFontType,
    text: str,
    size: float,
    x: float,
    y: float,
) -> tuple[str, float]:
    """Convert `text` to an SVG path. `y` is the baseline. Returns (d, width)."""
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    units = float(font["head"].unitsPerEm)
    scale = size / units
    cursor = x
    chunks: list[str] = []
    for char in text:
        if char == " ":
            if "space" in glyph_set:
                space = glyph_set["space"].width * scale
            else:
                space = size * 0.33
            cursor += space
            continue
        name = cmap.get(ord(char))
        if name is None:
            cursor += size * 0.5
            continue
        glyph = glyph_set[name]
        pen = SVGPathPen(glyph_set)
        transformed = TransformPen(pen, (scale, 0, 0, -scale, cursor, y))
        glyph.draw(transformed)
        command = _round_path(pen.getCommands())
        if command:
            chunks.append(command)
        cursor += glyph.width * scale
    return " ".join(chunks), cursor - x


def text_width(font: TTFontType, text: str, size: float) -> float:
    """Advance width of `text` without keeping the outline."""
    return outline_text(font, text, size, 0, 0)[1]


def _round_path(d: str) -> str:
    """Keep outlined paths small enough for a profile README."""
    return re.sub(r"-?\d+\.\d+", lambda match: f"{float(match.group()):.1f}", d)


# Glyphs outlined once per document and placed with <use>. Text-heavy modules
# repeat the same few dozen glyphs hundreds of times, so this keeps each SVG
# a fraction of the size of fully expanded paths.
_GLYPH_DEFS: dict[tuple[int, str, float], tuple[str, str]] = {}


def _glyph_ref(font: TTFontType, name: str, size: float) -> str:
    """Register one glyph at `size` with its origin on the baseline; return its id."""
    key = (id(font), name, size)
    if key not in _GLYPH_DEFS:
        glyph_set = font.getGlyphSet()
        scale = size / float(font["head"].unitsPerEm)
        pen = SVGPathPen(glyph_set)
        glyph_set[name].draw(TransformPen(pen, (scale, 0, 0, -scale, 0, 0)))
        _GLYPH_DEFS[key] = (f"g{len(_GLYPH_DEFS)}", _round_path(pen.getCommands()))
    return _GLYPH_DEFS[key][0]


def type_run(
    font: TTFontType,
    text: str,
    size: float,
    x: float,
    y: float,
    fill: str,
    element_id: str,
    extra: str = "",
) -> tuple[str, float]:
    """Outlined text as <use> references into the document's glyph defs."""
    cmap = font.getBestCmap()
    glyph_set = font.getGlyphSet()
    scale = size / float(font["head"].unitsPerEm)
    cursor = x
    uses: list[str] = []
    for char in text:
        if char == " ":
            space = glyph_set["space"].width if "space" in glyph_set else 0.0
            cursor += space * scale if space else size * 0.33
            continue
        name = cmap.get(ord(char))
        if name is None:
            cursor += size * 0.5
            continue
        ref = _glyph_ref(font, name, size)
        uses.append(f'<use href="#{ref}" x="{cursor:.1f}" y="{y:.1f}"/>')
        cursor += glyph_set[name].width * scale
    tail = f" {extra}" if extra else ""
    markup = f'<g id="{element_id}" fill="{fill}"{tail}>{"".join(uses)}</g>'
    return markup, cursor - x


def _svg_doc(width: float, height: float, body: str) -> str:
    """Wrap inner markup in a transparent SVG document with its glyph defs."""
    defs = "".join(
        f'<path id="{ref}" d="{d}"/>' for ref, d in _GLYPH_DEFS.values() if d
    )
    _GLYPH_DEFS.clear()
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width:g} {height:g}" width="{width:g}" height="{height:g}" '
        f'role="img" fill="none">\n<defs>{defs}</defs>\n{body}\n</svg>\n'
    )


def _path(d: str, fill: str, element_id: str, extra: str = "") -> str:
    """A filled path."""
    tail = f" {extra}" if extra else ""
    return f'<path id="{element_id}" d="{d}" fill="{fill}"{tail}/>'


def mono_label(
    text: str,
    size: float,
    x: float,
    y: float,
    fill: str,
    element_id: str,
    *,
    anchor_end: bool = False,
) -> tuple[str, float]:
    """Outlined mono text, optionally right-aligned on `x`. Returns (markup, w)."""
    mono = plex_mono()
    width = text_width(mono, text, size)
    start = x - width if anchor_end else x
    markup, _ = type_run(mono, text, size, start, y, fill, element_id)
    return markup, width


def pulse_dot(cx: float, cy: float, fill: str, element_id: str) -> str:
    """Solid dot with a slow expanding ring — the page's heartbeat."""
    return (
        f'<g id="{element_id}">'
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.5" fill="{fill}"/>'
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.5" fill="none" '
        f'stroke="{fill}" stroke-width="1.2" opacity="0">'
        f'<animate attributeName="r" values="3.5;11" dur="2.4s" '
        f'repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0.7;0" dur="2.4s" '
        f'repeatCount="indefinite"/>'
        f"</circle>"
        f"</g>"
    )


def build_now(palette: Theme, line: str) -> str:
    """Weekly now strip: live dot, NOW, and the focus line from content/now.yml."""
    focus = line.strip()
    if not focus:
        raise ValueError("now line is empty")
    label, _ = mono_label("NOW", 13, 62, 30, palette["ACCENT"], "now-label")
    text, width = mono_label(focus, 15, 112, 30, palette["INK"], "now-line")
    stamp = ""
    if 112 + width < 640:
        stamp, _ = mono_label(
            "refreshed weekly by CI",
            11,
            840,
            30,
            palette["MUTED"],
            "now-stamp",
            anchor_end=True,
        )
    body = (
        f'<path d="M40 1 H840 M40 47 H840" stroke="{palette["HAIRLINE"]}" '
        f'stroke-width="1"/>'
        f"{pulse_dot(46, 25, palette['ACCENT'], 'now-dot')}"
        f"{label}{text}{stamp}"
    )
    return _svg_doc(880, 48, body)


def write_themed(stem: str, build: Callable[[Theme], str]) -> None:
    """Write `{stem}-light.svg` and `{stem}-dark.svg` into dist."""
    tokens = load_tokens()
    DIST.mkdir(parents=True, exist_ok=True)
    for theme_name, palette in tokens.items():
        path = DIST / f"{stem}-{theme_name}.svg"
        path.write_text(build(palette), encoding="utf-8")
