"""Webpage modules: isometric glyphs, colored type, and living page sections."""

from __future__ import annotations

from fontTools.ttLib.ttFont import TTFont as TTFontType

from scripts.datum import (
    Theme,
    _path,
    _svg_doc,
    newsreader,
    outline_text,
    plex_mono,
)


def defs_3d(palette: Theme, prefix: str) -> str:
    """Lighting, glow, and a soft shadow shared by every page module."""
    return (
        f"<defs>"
        f'<linearGradient id="{prefix}-top" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{palette["LIGHT"]}"/>'
        f'<stop offset="1" stop-color="{palette["FACE"]}"/>'
        f"</linearGradient>"
        f'<linearGradient id="{prefix}-left" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{palette["FACE"]}"/>'
        f'<stop offset="1" stop-color="{palette["SHADE"]}"/>'
        f"</linearGradient>"
        f'<linearGradient id="{prefix}-right" x1="1" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{palette["FILAMENT"]}"/>'
        f'<stop offset="1" stop-color="{palette["DEPTH"]}"/>'
        f"</linearGradient>"
        f'<radialGradient id="{prefix}-glow" cx="40%" cy="30%" r="60%">'
        f'<stop offset="0" stop-color="{palette["GOLD"]}" stop-opacity="0.45"/>'
        f'<stop offset="1" stop-color="{palette["FILAMENT"]}" stop-opacity="0"/>'
        f"</radialGradient>"
        f'<filter id="{prefix}-soft" x="-30%" y="-30%" width="160%" height="160%">'
        f'<feGaussianBlur in="SourceAlpha" stdDeviation="1.8" result="b"/>'
        f'<feOffset dy="1.2" result="o"/>'
        f'<feColorMatrix result="s" '
        f'values="0 0 0 0 0.45 0 0 0 0 0.22 0 0 0 0 0.08 0 0 0 0.28 0"/>'
        f'<feMerge><feMergeNode in="s"/><feMergeNode in="SourceGraphic"/></feMerge>'
        f"</filter>"
        f"</defs>"
    )


def iso_box(cx: float, cy: float, edge: float, height: float, prefix: str) -> str:
    """One isometric block. `cx,cy` is the top diamond center."""
    a = edge
    h = height
    top = (
        f"M{cx:.1f},{cy:.1f} L{cx + a:.1f},{cy + a * 0.5:.1f} "
        f"L{cx:.1f},{cy + a:.1f} L{cx - a:.1f},{cy + a * 0.5:.1f} Z"
    )
    right = (
        f"M{cx:.1f},{cy + a:.1f} L{cx + a:.1f},{cy + a * 0.5:.1f} "
        f"L{cx + a:.1f},{cy + a * 0.5 + h:.1f} L{cx:.1f},{cy + a + h:.1f} Z"
    )
    left = (
        f"M{cx:.1f},{cy + a:.1f} L{cx - a:.1f},{cy + a * 0.5:.1f} "
        f"L{cx - a:.1f},{cy + a * 0.5 + h:.1f} L{cx:.1f},{cy + a + h:.1f} Z"
    )
    return (
        f'<path d="{top}" fill="url(#{prefix}-top)"/>'
        f'<path d="{right}" fill="url(#{prefix}-right)"/>'
        f'<path d="{left}" fill="url(#{prefix}-left)"/>'
    )


def rail(palette: Theme, height: float) -> str:
    """Left page spine so every module reads as one site column."""
    return (
        f'<path d="M18 8 V{height - 8:.0f}" stroke="{palette["HAIRLINE"]}" '
        f'stroke-width="1"/>'
        f'<circle cx="18" cy="18" r="3.2" fill="{palette["FILAMENT"]}">'
        f'<animate attributeName="opacity" values="0.55;1;0.55" '
        f'dur="11s" repeatCount="indefinite"/>'
        f"</circle>"
    )


def wrap_text(font: TTFontType, text: str, size: float, max_width: float) -> list[str]:
    """Greedy wrap using the same advance as outlined type."""
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        _, width = outline_text(font, trial, size, 0, 0)
        if width > max_width and current:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return lines


def outlined_block(
    font: TTFontType,
    text: str,
    size: float,
    x: float,
    y: float,
    fill: str,
    element_id: str,
    *,
    max_width: float,
    leading: float,
) -> tuple[str, float]:
    """Draw wrapped outlined copy. Returns markup and the last baseline."""
    lines = wrap_text(font, text, size, max_width)
    parts: list[str] = []
    baseline = y
    for index, line in enumerate(lines, start=1):
        d, _ = outline_text(font, line, size, x, baseline)
        parts.append(_path(d, fill, f"{element_id}-{index}"))
        baseline += leading
    return "".join(parts), baseline - leading


def with_float(inner: str, element_id: str, delay: str) -> str:
    """Wrap a mark so it breathes 2 units without losing its position."""
    return (
        f'<g id="{element_id}">{inner}'
        f'<animateTransform attributeName="transform" type="translate" '
        f'values="0 0; 0 -2; 0 0" dur="12s" begin="{delay}" '
        f'repeatCount="indefinite"/>'
        f"</g>"
    )


def glyph_loop(palette: Theme, prefix: str) -> str:
    """Three cycling blocks — agents that run the loop."""
    return (
        f'<g id="{prefix}-glyph" filter="url(#{prefix}-soft)">'
        f'<circle cx="36" cy="34" r="22" fill="url(#{prefix}-glow)"/>'
        f"{iso_box(28, 14, 11, 8, prefix)}"
        f"{iso_box(44, 22, 11, 8, prefix)}"
        f"{iso_box(36, 30, 11, 8, prefix)}"
        f'<path d="M18 28 C 20 16 52 14 54 30" fill="none" '
        f'stroke="{palette["FILAMENT"]}" stroke-width="1.6" '
        f'stroke-linecap="round"/>'
        f'<circle cx="54" cy="30" r="2.1" fill="{palette["GOLD"]}">'
        f'<animate attributeName="opacity" values="0.5;1;0.5" '
        f'dur="10s" repeatCount="indefinite"/>'
        f"</circle>"
        f"</g>"
    )


def glyph_search(palette: Theme, prefix: str) -> str:
    """Fanned catalog cards plus a copper lens."""
    return (
        f'<g id="{prefix}-glyph" filter="url(#{prefix}-soft)">'
        f"{iso_box(30, 16, 14, 4, prefix)}"
        f"{iso_box(36, 20, 14, 4, prefix)}"
        f"{iso_box(42, 24, 14, 4, prefix)}"
        f'<circle cx="50" cy="40" r="9" fill="none" '
        f'stroke="{palette["FILAMENT"]}" stroke-width="2.2"/>'
        f'<path d="M56 46 L62 54" stroke="{palette["GOLD"]}" '
        f'stroke-width="2.4" stroke-linecap="round"/>'
        f"</g>"
    )


def glyph_roof(palette: Theme, prefix: str) -> str:
    """Isometric gable — roofs from the air."""
    ridge = "M36,12 L54,22 L36,32 L18,22 Z"
    face = "M36,32 L54,22 L54,42 L36,52 Z"
    shade = "M36,32 L18,22 L18,42 L36,52 Z"
    return (
        f'<g id="{prefix}-glyph" filter="url(#{prefix}-soft)">'
        f'<path d="{ridge}" fill="url(#{prefix}-top)"/>'
        f'<path d="{face}" fill="url(#{prefix}-right)"/>'
        f'<path d="{shade}" fill="url(#{prefix}-left)"/>'
        f'<path d="M22 30 L36 22 L50 30" fill="none" '
        f'stroke="{palette["GOLD"]}" stroke-width="1.3"/>'
        f"</g>"
    )


def glyph_chat(palette: Theme, prefix: str) -> str:
    """Two speech volumes — English and Hinglish."""
    return (
        f'<g id="{prefix}-glyph" filter="url(#{prefix}-soft)">'
        f"{iso_box(28, 16, 13, 9, prefix)}"
        f"{iso_box(44, 24, 12, 8, prefix)}"
        f'<circle cx="26" cy="24" r="1.6" fill="{palette["GOLD"]}"/>'
        f'<circle cx="32" cy="27" r="1.6" fill="{palette["FILAMENT"]}"/>'
        f'<circle cx="38" cy="30" r="1.6" fill="{palette["GOLD"]}"/>'
        f"</g>"
    )


def glyph_ocr(palette: Theme, prefix: str) -> str:
    """A page with a scanning filament."""
    return (
        f'<g id="{prefix}-glyph" filter="url(#{prefix}-soft)">'
        f"{iso_box(36, 12, 16, 3, prefix)}"
        f'<path d="M22 28 H50" stroke="{palette["MUTED"]}" stroke-width="1.2"/>'
        f'<path d="M24 34 H46" stroke="{palette["MUTED"]}" stroke-width="1.2"/>'
        f'<path d="M26 40 H42" stroke="{palette["MUTED"]}" stroke-width="1.2"/>'
        f'<line x1="20" y1="22" x2="52" y2="22" stroke="{palette["FILAMENT"]}" '
        f'stroke-width="2" stroke-linecap="round">'
        f'<animate attributeName="y1" values="22;44;22" dur="8s" '
        f'repeatCount="indefinite"/>'
        f'<animate attributeName="y2" values="22;44;22" dur="8s" '
        f'repeatCount="indefinite"/>'
        f"</line>"
        f"</g>"
    )


def glyph_cart(palette: Theme, prefix: str) -> str:
    """Isometric cart for the CES live demo."""
    return (
        f'<g id="{prefix}-glyph" filter="url(#{prefix}-soft)">'
        f"{iso_box(36, 18, 16, 10, prefix)}"
        f'<circle cx="26" cy="48" r="5" fill="{palette["SHADE"]}"/>'
        f'<circle cx="46" cy="48" r="5" fill="{palette["SHADE"]}"/>'
        f'<circle cx="26" cy="48" r="2.2" fill="{palette["GOLD"]}"/>'
        f'<circle cx="46" cy="48" r="2.2" fill="{palette["GOLD"]}"/>'
        f'<path d="M20 22 L36 14 L52 22" fill="none" '
        f'stroke="{palette["FILAMENT"]}" stroke-width="1.5"/>'
        f"</g>"
    )


def glyph_mail(palette: Theme, prefix: str) -> str:
    """Isometric envelope."""
    return (
        f'<g id="{prefix}-glyph" filter="url(#{prefix}-soft)">'
        f"{iso_box(36, 18, 18, 6, prefix)}"
        f'<path d="M20 28 L36 38 L52 28" fill="none" '
        f'stroke="{palette["GOLD"]}" stroke-width="1.8" '
        f'stroke-linecap="round"/>'
        f"</g>"
    )


def glyph_record(palette: Theme, prefix: str) -> str:
    """Stacked slabs — what can be shown."""
    return (
        f'<g id="{prefix}-glyph" filter="url(#{prefix}-soft)">'
        f"{iso_box(36, 10, 15, 5, prefix)}"
        f"{iso_box(36, 18, 15, 5, prefix)}"
        f"{iso_box(36, 26, 15, 5, prefix)}"
        f'<circle cx="36" cy="20" r="2" fill="{palette["GOLD"]}"/>'
        f"</g>"
    )


GLYPHS = {
    "loop": glyph_loop,
    "search": glyph_search,
    "roof": glyph_roof,
    "chat": glyph_chat,
    "ocr": glyph_ocr,
    "cart": glyph_cart,
    "mail": glyph_mail,
    "record": glyph_record,
}


def build_emoji(palette: Theme, kind: str) -> str:
    """64×64 custom emoji. One 3D object, already complete on the first frame."""
    prefix = f"e-{kind}"
    body = (
        f"{defs_3d(palette, prefix)}"
        f'<rect x="4" y="6" width="56" height="52" rx="0" fill="{palette["BASIN"]}"/>'
        f"{with_float(GLYPHS[kind](palette, prefix), f'{prefix}-float', '0s')}"
    )
    return _svg_doc(64, 64, body)


def heading_3d(palette: Theme, text: str, x: float, y: float, element_id: str) -> str:
    """Extruded mono label — a tiny 3D plaque."""
    mono = plex_mono()
    front, width = outline_text(mono, text, 18, x, y)
    depth, _ = outline_text(mono, text, 18, x + 1.4, y + 1.4)
    return (
        f"{_path(depth, palette['SHADE'], f'{element_id}-depth')}"
        f"{_path(front, palette['INK'], element_id)}"
        f'<path d="M{x:.1f} {y + 8:.1f} H{x + width:.1f}" '
        f'stroke="{palette["FILAMENT"]}" stroke-width="2" stroke-linecap="round"/>'
    )


def build_frame(palette: Theme) -> str:
    """Lede as a page module: 3D datum sculpture plus the intro copy."""
    regular = newsreader(italic=False)
    prefix = "frame"
    body_copy = (
        "I run Immovable Tech. Before that I spent eight years putting models "
        "into products that already had users — search, KYC, roofs measured "
        "from the air, assistants that had to answer in two languages. I care "
        "about the part after the demo: latency, evals, the bill, whether it "
        "still works on a Monday."
    )
    block, last = outlined_block(
        regular,
        body_copy,
        16,
        200,
        88,
        palette["INK"],
        "lede",
        max_width=640,
        leading=22,
    )
    sculpture = with_float(
        f'<g filter="url(#{prefix}-soft)">'
        f'<circle cx="108" cy="128" r="62" fill="url(#{prefix}-glow)"/>'
        f'<circle cx="108" cy="128" r="44" fill="{palette["BASIN"]}"/>'
        f"{iso_box(108, 96, 22, 16, prefix)}"
        f'<path d="M78 90 C 90 106 98 118 108 128" fill="none" '
        f'stroke="{palette["FILAMENT"]}" stroke-width="2.2" '
        f'stroke-linecap="round"/>'
        f'<circle cx="108" cy="128" r="4" fill="{palette["GOLD"]}">'
        f'<animate attributeName="opacity" values="0.55;1;0.55" '
        f'dur="12s" repeatCount="indefinite"/>'
        f"</circle>"
        f"</g>",
        "sculpture",
        "0s",
    )
    studio, _ = outline_text(plex_mono(), "IMMOVABLE TECH", 12, 200, last + 28)
    height = int(last + 52)
    body = (
        f"{defs_3d(palette, prefix)}"
        f"{rail(palette, float(height))}"
        f"{sculpture}"
        f"{block}"
        f"{_path(studio, palette['GOLD'], 'studio')}"
    )
    return _svg_doc(880, height, body)


SYSTEMS = (
    (
        "loop",
        "Immovable Tech",
        (
            "Agents that run the loop, not the slide. LangGraph + LangSmith, "
            "graph + vector RAG, models tuned on the domain, evals you can "
            "read later."
        ),
    ),
    (
        "search",
        "Catalog search at 5,000 QPS",
        (
            "Semantic matching and learn-to-rank. Click-through +50%, "
            "revenue +10%, Milvus underneath."
        ),
    ),
    (
        "roof",
        "Roofs from the air",
        (
            "Line detection 28% → 59%. Facets at 86% mIOU. Triton + INT8, "
            "25% faster, 30% less VRAM."
        ),
    ),
    (
        "chat",
        "A national-scale assistant",
        (
            "English and Hinglish, thousands of chats a day. The KYC face "
            "stack next to it cut manual review about 25%."
        ),
    ),
    (
        "ocr",
        "OCR that beat the API I was paying for",
        (
            "+12% on ICDAR 2013 versus Google Vision, at a tenth the infra. "
            "BERT on the correction pass."
        ),
    ),
    (
        "cart",
        "CES 2019",
        (
            "Gesture, face, collision tracking in a live golf-cart demo. "
            "The public repo is a dummy sketch, not the show build."
        ),
    ),
)


def build_systems(palette: Theme) -> str:
    """Six selected systems as a feature list, each with a 3D glyph."""
    prefix = "sys"
    regular = newsreader(italic=False)
    parts = [
        defs_3d(palette, prefix),
        rail(palette, 780),
        heading_3d(palette, "WORK", 44, 36, "work-head"),
    ]
    y = 64.0
    for index, (kind, title, blurb) in enumerate(SYSTEMS, start=1):
        glyph_id = f"{prefix}-{kind}"
        glyph = GLYPHS[kind](palette, f"{prefix}{index}")
        title_d, _ = outline_text(regular, title, 20, 120, y + 28)
        blurb_markup, last = outlined_block(
            regular,
            blurb,
            14,
            120,
            y + 50,
            palette["MUTED"],
            f"blurb-{index}",
            max_width=720,
            leading=18,
        )
        parts.append(
            f'<g transform="translate(36 {y:.1f}) scale(0.92)">'
            f"{defs_3d(palette, f'{prefix}{index}')}"
            f"{with_float(glyph, glyph_id, f'{0.4 * index:.1f}s')}"
            f"</g>"
        )
        parts.append(_path(title_d, palette["INK"], f"title-{index}"))
        parts.append(blurb_markup)
        shelf = last + 16
        parts.append(
            f'<path d="M44 {shelf:.1f} H844" stroke="{palette["HAIRLINE"]}" '
            f'stroke-width="1"/>'
        )
        y = shelf + 8
    return _svg_doc(880, int(y + 24), "".join(parts))


def build_take(palette: Theme) -> str:
    """Founder CTA as a 3D plaque, not a grey heading."""
    prefix = "take"
    regular = newsreader(italic=False)
    head = heading_3d(palette, "HOW I TAKE WORK", 120, 40, "take-head")
    copy = (
        "I take 0→1 AI products and the messy ones that already exist. "
        "Discovery through deploy. If you need a deck, I’m the wrong person. "
        "If you need a system that is still correct in six months, email me."
    )
    block, _ = outlined_block(
        regular,
        copy,
        16,
        120,
        72,
        palette["INK"],
        "take-copy",
        max_width=720,
        leading=22,
    )
    mail = (
        f'<g transform="translate(36 48) scale(0.9)">'
        f"{with_float(glyph_mail(palette, prefix), 'mail-mark', '0s')}"
        f"</g>"
    )
    body = f"{defs_3d(palette, prefix)}{rail(palette, 188)}{mail}{head}{block}"
    return _svg_doc(880, 196, body)


CHIP_ROWS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "AGENTS",
        (
            "LangGraph",
            "LangSmith",
            "LangChain",
            "CrewAI",
            "MCP",
            "Agents SDK",
        ),
    ),
    (
        "MODELS",
        ("PyTorch", "Transformers", "LoRA", "Llama", "FLUX"),
    ),
    (
        "RETRIEVE",
        ("Neo4j", "Milvus", "Pinecone", "RAG"),
    ),
    (
        "SERVE",
        ("FastAPI", "Docker", "ONNX", "TensorRT", "Triton", "MLflow"),
    ),
    (
        "CLOUD",
        ("AWS", "SageMaker", "Lambda", "GCP", "Vertex", "Azure"),
    ),
)


def build_chips(palette: Theme) -> str:
    """Full bench as isometric tiles, grouped the way the work is staffed."""
    prefix = "chip"
    mono = plex_mono()
    parts = [defs_3d(palette, prefix)]
    parts.append(heading_3d(palette, "STACK", 44, 36, "stack-head"))
    x = 48.0
    y = 64.0
    chip_index = 0
    for row_index, (group, labels) in enumerate(CHIP_ROWS, start=1):
        group_d, _ = outline_text(mono, group, 12, 48, y + 12)
        parts.append(_path(group_d, palette["GOLD"], f"chip-group-{row_index}"))
        y += 22
        x = 48.0
        for label in labels:
            chip_index += 1
            _, width = outline_text(mono, label, 13, 0, 0)
            label_d, _ = outline_text(mono, label, 13, 12, 18)
            tile_w = max(width + 28, 80)
            if x + tile_w > 840:
                x = 48.0
                y += 44.0
            parts.append(
                f'<g id="chip-{chip_index}" '
                f'transform="translate({x:.1f} {y:.1f})">'
                f'<path d="M0 10 L10 0 H{tile_w:.1f} L{tile_w - 10:.1f} 10 Z" '
                f'fill="url(#{prefix}-top)"/>'
                f'<path d="M0 10 V26 L{tile_w - 10:.1f} 26 V10 Z" '
                f'fill="url(#{prefix}-left)"/>'
                f'<path d="M{tile_w - 10:.1f} 10 L{tile_w:.1f} 0 '
                f'V16 L{tile_w - 10:.1f} 26 Z" '
                f'fill="url(#{prefix}-right)"/>'
                f"{_path(label_d, palette['INK'], f'chip-t-{chip_index}')}"
                f'<animateTransform attributeName="transform" '
                f'type="translate" values="{x:.1f} {y:.1f}; {x:.1f} {y - 2:.1f}; '
                f'{x:.1f} {y:.1f}" dur="{10 + chip_index}s" '
                f'repeatCount="indefinite"/>'
                f"</g>"
            )
            x += tile_w + 12
        y += 50.0
    height = int(y + 16)
    parts.insert(1, rail(palette, float(height)))
    return _svg_doc(880, height, "".join(parts))


def build_record(palette: Theme) -> str:
    """On the record — closed work, then the public artifacts as type."""
    prefix = "rec"
    regular = newsreader(italic=False)
    head = heading_3d(palette, "ON THE RECORD", 120, 40, "rec-head")
    copy = (
        "Most of the work above is closed. What I can show: a Differentiable "
        "Binarization implementation, an OpenVINO OCR path, and a local "
        "LangGraph assistant. The CES cart has a dummy sketch, not the show "
        "build. I used to answer face-embedding questions on Stack Overflow."
    )
    block, _ = outlined_block(
        regular,
        copy,
        15,
        120,
        72,
        palette["MUTED"],
        "rec-copy",
        max_width=720,
        leading=20,
    )
    mark = (
        f'<g transform="translate(36 48) scale(0.9)">'
        f"{with_float(glyph_record(palette, prefix), 'rec-mark', '0s')}"
        f"</g>"
    )
    body = f"{defs_3d(palette, prefix)}{rail(palette, 196)}{mark}{head}{block}"
    return _svg_doc(880, 204, body)


def build_reach(palette: Theme) -> str:
    """Contact dock. The real links stay in markdown under this strip."""
    prefix = "reach"
    mono = plex_mono()
    mail, _ = outline_text(mono, "rishabpal.work@gmail.com", 16, 120, 78)
    li, _ = outline_text(mono, "LinkedIn", 16, 120, 108)
    studio, _ = outline_text(mono, "Immovable Tech", 16, 120, 138)
    head = heading_3d(palette, "REACH", 120, 40, "reach-head")
    mark = (
        f'<g transform="translate(36 52) scale(0.9)">'
        f"{with_float(glyph_mail(palette, prefix), 'reach-mark', '0s')}"
        f"</g>"
    )
    body = (
        f"{defs_3d(palette, prefix)}"
        f"{rail(palette, 168)}"
        f"{mark}"
        f"{head}"
        f"{_path(mail, palette['INK'], 'reach-mail')}"
        f"{_path(li, palette['FILAMENT'], 'reach-li')}"
        f"{_path(studio, palette['GOLD'], 'reach-studio')}"
    )
    return _svg_doc(880, 168, body)
