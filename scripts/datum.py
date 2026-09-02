"""Living Datum primitives: tokens, outlined type, and SVG compositions."""

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
SRC: Final[Path] = ROOT / "assets" / "src"

Theme = dict[str, str]


def load_tokens() -> dict[str, Theme]:
    """Read the light and dark filament palettes."""
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


def _round_path(d: str) -> str:
    """Keep outlined paths small enough for a profile README."""
    return re.sub(r"-?\d+\.\d+", lambda match: f"{float(match.group()):.1f}", d)


def _svg_doc(width: int, height: int, body: str) -> str:
    """Wrap inner markup in a transparent SVG document."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'role="img" fill="none">\n{body}\n</svg>\n'
    )


def _path(d: str, fill: str, element_id: str) -> str:
    """A filled outlined-type path."""
    return f'<path id="{element_id}" d="{d}" fill="{fill}"/>'


def sigil_group(
    palette: Theme,
    x: float,
    y: float,
    scale: float,
    *,
    pulse: bool,
    element_id: str,
) -> str:
    """Basin, crosshair, loss curve, and optional filament tick."""
    tick = ""
    if pulse:
        tick = (
            f'<circle id="{element_id}-tick" cx="24" cy="28" r="1.6" '
            f'fill="{palette["FILAMENT"]}">'
            f'<animate attributeName="opacity" values="0.55;1;0.55" '
            f'dur="12s" repeatCount="indefinite"/>'
            f'<animate attributeName="cy" values="28;26.5;28" '
            f'dur="12s" repeatCount="indefinite"/>'
            f"</circle>"
        )
    else:
        tick = (
            f'<circle id="{element_id}-tick" cx="24" cy="28" r="1.6" '
            f'fill="{palette["FILAMENT"]}"/>'
        )
    inner = (
        f'<circle id="{element_id}-basin" cx="24" cy="28" r="13" '
        f'fill="{palette["BASIN"]}"/>'
        f'<path id="{element_id}-horizon" pathLength="1" '
        f'd="M6 9 C 12 18 18 24 24 28" '
        f'stroke="{palette["FILAMENT"]}" stroke-width="1.4" '
        f'stroke-linecap="round" fill="none"/>'
        f'<path id="{element_id}-cross" '
        f'd="M16 28 H32 M24 21 V35" '
        f'stroke="{palette["INK"]}" stroke-width="1.1" '
        f'stroke-linecap="round"/>'
        f"{tick}"
    )
    return (
        f'<g id="{element_id}" transform="translate({x:.2f} {y:.2f}) '
        f'scale({scale:.4f})">{inner}</g>'
    )


def build_sigil(palette: Theme) -> str:
    """48×48 mark, no type."""
    body = sigil_group(palette, 0, 0, 1.0, pulse=True, element_id="datum")
    return _svg_doc(48, 48, body)


def build_hero(palette: Theme) -> str:
    """Hook as outlined serif over a loss-curve horizon."""
    regular = newsreader(italic=False)
    italic = newsreader(italic=True)
    line1, w1 = outline_text(regular, "My loss function", 46, 40, 78)
    line2, w2 = outline_text(regular, "in life is", 46, 40, 136)
    line3, w3 = outline_text(italic, "feeling alive.", 52, 40, 204)
    sigil_x = 40 + w3 + 18
    t_mark, _ = outline_text(plex_mono(), "t", 18, 40, 304)
    l_mark, _ = outline_text(plex_mono(), "L", 18, 848, 304)
    basin_x = 40 + w3
    horizon = (
        f'<path id="axis" d="M40 296 H840" '
        f'stroke="{palette["HAIRLINE"]}" stroke-width="1" fill="none"/>'
        f'<path id="horizon" pathLength="1" '
        f'd="M40 248 C 120 248 200 260 {basin_x:.1f} 296" '
        f'stroke="{palette["FILAMENT"]}" stroke-width="1.35" '
        f'stroke-linecap="round" fill="none" opacity="0.85"/>'
        f'<circle id="basin" cx="{basin_x:.1f}" cy="296" r="11" '
        f'fill="{palette["BASIN"]}"/>'
        f'<circle id="tick" cx="{basin_x:.1f}" cy="296" r="2.2" '
        f'fill="{palette["FILAMENT"]}">'
        f'<animate attributeName="opacity" values="0.55;1;0.55" '
        f'dur="12s" repeatCount="indefinite"/>'
        f'<animate attributeName="cy" values="296;293.8;296" '
        f'dur="12s" repeatCount="indefinite"/>'
        f"</circle>"
    )
    body = (
        f"{_path(line1, palette['INK'], 'hook-1')}"
        f"{_path(line2, palette['INK'], 'hook-2')}"
        f"{_path(line3, palette['FILAMENT'], 'hook')}"
        f"{sigil_group(palette, sigil_x, 168, 0.72, pulse=False, element_id='datum')}"
        f"{horizon}"
        f"{_path(t_mark, palette['MUTED'], 'axis-t')}"
        f"{_path(l_mark, palette['MUTED'], 'axis-l')}"
    )
    _ = (w1, w2)
    return _svg_doc(880, 320, body)


def build_act(palette: Theme) -> str:
    """SEE · CHOOSE · ACT on one polyline, token parked on ACT first."""
    mono = plex_mono()
    see, see_w = outline_text(mono, "SEE", 28, 48, 52)
    choose, choose_w = outline_text(mono, "CHOOSE", 28, 360, 52)
    act, act_w = outline_text(mono, "ACT", 28, 760, 52)
    see_cx = 48 + see_w / 2
    choose_cx = 360 + choose_w / 2
    act_cx = 760 + act_w / 2
    motion = (
        f'<path id="act-rail" pathLength="1" '
        f'd="M{act_cx:.1f} 28 L{see_cx:.1f} 28 L{choose_cx:.1f} 28 L{act_cx:.1f} 28" '
        f'stroke="{palette["HAIRLINE"]}" stroke-width="1" fill="none"/>'
        f'<rect id="tick" x="-2.5" y="-2.5" width="5" height="5" '
        f'fill="{palette["FILAMENT"]}">'
        f'<animateMotion dur="14s" repeatCount="indefinite" rotate="0" '
        f'keyPoints="0;0;0.33;0.66;1" keyTimes="0;0.4;0.6;0.8;1" '
        f'calcMode="linear">'
        f'<mpath href="#act-rail"/>'
        f"</animateMotion>"
        f"</rect>"
    )
    body = (
        f"{_path(see, palette['MUTED'], 'see')}"
        f"{_path(choose, palette['MUTED'], 'choose')}"
        f"{_path(act, palette['FILAMENT'], 'act')}"
        f"{motion}"
    )
    return _svg_doc(880, 88, body)


def build_work(palette: Theme) -> str:
    """Three stacked metric rows. No cards."""
    mono = plex_mono()
    rows = (
        ("01", "+50% CTR", "catalog search", 58),
        ("02", "28% → 59%", "aerial lines", 144),
        ("03", "CES '19", "live demo", 230),
    )
    parts: list[str] = []
    for index, (num, metric, domain, baseline) in enumerate(rows, start=1):
        num_d, _ = outline_text(mono, num, 18, 40, baseline)
        metric_d, _ = outline_text(mono, metric, 38, 110, baseline)
        domain_d, _ = outline_text(mono, domain, 20, 620, baseline)
        parts.append(_path(num_d, palette["MUTED"], f"idx-{index}"))
        parts.append(_path(metric_d, palette["FILAMENT"], f"metric-{index}"))
        parts.append(_path(domain_d, palette["MUTED"], f"domain-{index}"))
        if index < 3:
            y = baseline + 28
            parts.append(
                f'<path d="M40 {y} H840" stroke="{palette["HAIRLINE"]}" '
                f'stroke-width="1"/>'
            )
    return _svg_doc(880, 260, "".join(parts))


def build_stack(palette: Theme) -> str:
    """Five nodes on a horizontal spine."""
    mono = plex_mono()
    labels = ("AGENTS", "MODELS", "DATA", "SERVE", "EVAL")
    xs = (80.0, 260.0, 440.0, 620.0, 800.0)
    nodes: list[str] = [
        f'<path id="spine" d="M80 64 H800" stroke="{palette["HAIRLINE"]}" '
        f'stroke-width="1"/>'
    ]
    for i, (label, x) in enumerate(zip(labels, xs, strict=True), start=1):
        d, width = outline_text(mono, label, 16, x - 40, 118)
        # Center the label under the node as much as the advance allows.
        centered, _ = outline_text(mono, label, 16, x - width / 2, 118)
        _ = d
        nodes.append(
            f'<circle id="node-{i}" cx="{x}" cy="64" r="7" '
            f'stroke="{palette["INK"]}" stroke-width="1.2" fill="none"/>'
        )
        nodes.append(_path(centered, palette["MUTED"], f"label-{i}"))
    nodes.append(
        f'<circle id="tick" cx="80" cy="64" r="2.2" fill="{palette["FILAMENT"]}">'
        f'<animate attributeName="cx" values="80;260;440;620;800;800;80" '
        f'keyTimes="0;0.18;0.36;0.54;0.72;0.88;1" dur="16s" '
        f'repeatCount="indefinite"/>'
        f"</circle>"
    )
    return _svg_doc(880, 168, "".join(nodes))


def build_now(palette: Theme, line: str) -> str:
    """Sigil + NOW + one injected focus line. First frame is fully visible."""
    focus = line.strip()
    if not focus:
        raise ValueError("now line is empty")
    mono = plex_mono()
    now_d, now_w = outline_text(mono, "NOW", 18, 56, 34)
    line_d, _ = outline_text(mono, focus, 18, 56 + now_w + 24, 34)
    body = (
        f"{sigil_group(palette, 8, 2, 0.75, pulse=True, element_id='datum')}"
        f"{_path(now_d, palette['MUTED'], 'now-label')}"
        f"{_path(line_d, palette['INK'], 'now-line')}"
    )
    return _svg_doc(880, 52, body)


def write_themed(stem: str, build: Callable[[Theme], str]) -> None:
    """Write `{stem}-light.svg` and `{stem}-dark.svg` into dist."""
    tokens = load_tokens()
    DIST.mkdir(parents=True, exist_ok=True)
    for theme_name, palette in tokens.items():
        path = DIST / f"{stem}-{theme_name}.svg"
        path.write_text(build(palette), encoding="utf-8")


def write_src_templates() -> None:
    """Tokenized geometry the compiler fills. Documents the system."""
    SRC.mkdir(parents=True, exist_ok=True)
    (SRC / "sigil.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">'
        '<circle id="basin" cx="24" cy="28" r="13" fill="{{BASIN}}"/>'
        '<path id="horizon" d="M6 9 C 12 18 18 24 24 28" '
        'stroke="{{FILAMENT}}" fill="none"/>'
        '<path id="cross" d="M16 28 H32 M24 21 V35" stroke="{{INK}}"/>'
        '<circle id="tick" cx="24" cy="28" r="1.6" fill="{{FILAMENT}}"/>'
        "</svg>\n",
        encoding="utf-8",
    )
    (SRC / "hero.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 320">'
        '<g id="hook" fill="{{INK}}"/>'
        '<path id="horizon" stroke="{{HAIRLINE}}"/>'
        '<circle id="basin" fill="{{BASIN}}"/>'
        '<circle id="tick" fill="{{FILAMENT}}"/>'
        "</svg>\n",
        encoding="utf-8",
    )
    (SRC / "act.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 88">'
        '<text fill="{{INK}}">SEE CHOOSE ACT</text>'
        '<path id="act-rail" stroke="{{HAIRLINE}}"/>'
        '<rect id="tick" fill="{{FILAMENT}}"/>'
        "</svg>\n",
        encoding="utf-8",
    )
    (SRC / "work.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 260">'
        '<text fill="{{INK}}">+50% CTR  28% → 59%  CES ’19</text>'
        "</svg>\n",
        encoding="utf-8",
    )
    (SRC / "stack.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 168">'
        '<path id="spine" stroke="{{HAIRLINE}}"/>'
        '<text fill="{{MUTED}}">AGENTS MODELS DATA SERVE EVAL</text>'
        "</svg>\n",
        encoding="utf-8",
    )
    (SRC / "now.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 52">'
        '<text fill="{{MUTED}}">NOW</text>'
        '<text id="now-line" fill="{{INK}}">{{NOW_LINE}}</text>'
        "</svg>\n",
        encoding="utf-8",
    )
