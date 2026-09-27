"""Profile modules: a forward pass, a trace, receipts, and the link dock."""

from __future__ import annotations

from typing import Final

from fontTools.ttLib.ttFont import TTFont as TTFontType

from scripts.datum import (
    Theme,
    _svg_doc,
    mono_label,
    newsreader,
    plex_mono,
    text_width,
    type_run,
)


def wrap_text(font: TTFontType, text: str, size: float, max_width: float) -> list[str]:
    """Greedy wrap using the same advance as outlined type."""
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if text_width(font, trial, size) > max_width and current:
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
    parts: list[str] = []
    baseline = y
    for index, line in enumerate(wrap_text(font, text, size, max_width), start=1):
        markup, _ = type_run(
            font, line, size, x, baseline, fill, f"{element_id}-{index}"
        )
        parts.append(markup)
        baseline += leading
    return "".join(parts), baseline - leading


def _k(value: float) -> str:
    """Format a keyTime or value compactly."""
    return f"{value:.4f}".rstrip("0").rstrip(".") or "0"


def appear(start: float, fade: float = 0.18, rise: float = 0.0) -> str:
    """Hidden until `start`, then fade (and optionally rise) in, once.

    Static renderers ignore SMIL, so the element's resting state is the
    finished frame and nothing is ever lost.
    """
    total = start + fade
    t0 = _k(start / total)
    anim = (
        f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{t0};1" '
        f'dur="{_k(total)}s" fill="freeze"/>'
    )
    if rise:
        anim += (
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 {rise};0 {rise};0 0" keyTimes="0;{t0};1" '
            f'dur="{_k(total)}s" fill="freeze"/>'
        )
    return anim


# --------------------------------------------------------------------------- hero

HERO_TOKENS: Final[tuple[tuple[str, bool, float], ...]] = (
    # (token, italic, p(token)) — leading spaces belong to the token, as in BPE.
    ("I", False, 0.94),
    (" build", False, 0.58),
    (" the", False, 0.97),
    (" part", False, 0.41),
    (" after", False, 0.86),
    (" the", False, 0.98),
    (" demo", True, 0.73),
    (".", False, 0.99),
)
QUERY: Final[int] = 6

# Attention from " demo" back over tokens 0..5, one row per head. The page
# cycles heads so the arcs keep re-weighting after the stream lands.
HEADS: Final[tuple[tuple[str, tuple[float, ...]], ...]] = (
    ("attn  L14 · H3", (0.12, 0.34, 0.05, 0.66, 0.95, 0.10)),
    ("attn  L14 · H7", (0.06, 0.08, 0.22, 0.12, 0.40, 0.95)),
    ("attn  L22 · H1", (0.92, 0.72, 0.06, 0.30, 0.12, 0.05)),
)

STREAM_START: Final[float] = 0.55
STREAM_STEP: Final[float] = 0.16
HEAD_CYCLE: Final[float] = 12.0

LEDE: Final[str] = (
    "I run Immovable Tech. Before that, eight years putting models into "
    "products that already had users — search, KYC, roofs measured from the "
    "air, assistants that answer in two languages."
)


def _head_keytimes() -> tuple[str, list[float]]:
    """Hold each head for most of its third, crossfade between them."""
    n = len(HEADS)
    times: list[float] = []
    for i in range(n):
        times.extend([i / n, (i + 0.78) / n])
    times.append(1.0)
    return ";".join(_k(t) for t in times), times


def _head_values(per_head: list[float]) -> str:
    """Expand one value per head into the hold/crossfade keyframe list."""
    values: list[float] = []
    for value in per_head:
        values.extend([value, value])
    values.append(per_head[0])
    return ";".join(_k(v) for v in values)


def build_hero(palette: Theme) -> str:
    """Name, a prompt, and a streamed answer drawn as tokens with attention."""
    regular = newsreader(italic=False)
    italic = newsreader(italic=True)
    size = 56.0
    baseline = 206.0
    chip_top = baseline - 0.76 * size
    chip_bottom = baseline + 0.27 * size
    gap = 3.0
    parts: list[str] = []

    name, _ = mono_label("RISHAB PAL", 13, 40, 34, palette["INK"], "name")
    role, _ = mono_label(
        "AI ENGINEER · FOUNDER, IMMOVABLE TECH",
        13,
        840,
        34,
        palette["MUTED"],
        "role",
        anchor_end=True,
    )
    chevron, chev_w = mono_label("›", 16, 40, 76, palette["ACCENT"], "chevron")
    prompt, _ = mono_label(
        "what do you build?", 15, 40 + chev_w + 8, 76, palette["MUTED"], "prompt"
    )
    parts += [
        name,
        role,
        f'<path d="M40 48 H840" stroke="{palette["HAIRLINE"]}" stroke-width="1"/>',
        chevron,
        prompt,
    ]

    # Lay tokens out first so arcs and the caret can reference their geometry.
    x = 48.0
    spans: list[tuple[float, float]] = []
    chips: list[str] = []
    for i, (token, is_italic, prob) in enumerate(HERO_TOKENS):
        font = italic if is_italic else regular
        glyphs, width = type_run(
            font,
            token,
            size,
            x,
            baseline,
            palette["ACCENT"] if i == QUERY else palette["INK"],
            f"tok-{i}-t",
        )
        left = x - (8.0 if i == 0 else 0.0)
        right = x + width + (8.0 if i == len(HERO_TOKENS) - 1 else 0.0)
        spans.append((left, right))
        hue = palette[f"T{i % 5 + 1}"]
        outline = ""
        if i == QUERY:
            outline = (
                f'<rect x="{left:.1f}" y="{chip_top:.1f}" '
                f'width="{right - left:.1f}" height="{chip_bottom - chip_top:.1f}" '
                f'rx="7" fill="none" stroke="{palette["ACCENT"]}" '
                f'stroke-width="1.4"/>'
            )
        start = STREAM_START + i * STREAM_STEP
        chips.append(
            f'<g id="tok-{i}">'
            f'<rect x="{left:.1f}" y="{chip_top:.1f}" width="{right - left:.1f}" '
            f'height="{chip_bottom - chip_top:.1f}" rx="7" fill="{hue}" '
            f'fill-opacity="{palette["TINT"]}"/>'
            f"{outline}"
            f"{glyphs}"
            f'<rect x="{left + 4:.1f}" y="{chip_bottom + 8:.1f}" '
            f'width="{max((right - left - 8) * prob, 2):.1f}" height="3" rx="1.5" '
            f'fill="{hue}"/>'
            f"{appear(start, rise=6)}"
            f"</g>"
        )
        x += width + gap
    stream_end = STREAM_START + len(HERO_TOKENS) * STREAM_STEP

    # Attention arcs from the query token back over its context.
    key_times, _ = _head_keytimes()
    qx = (spans[QUERY][0] + spans[QUERY][1]) / 2
    arc_base = chip_top - 5
    arcs: list[str] = []
    for j in range(QUERY):
        kx = (spans[j][0] + spans[j][1]) / 2
        apex = min(60.0, 14.0 + 0.1 * abs(qx - kx))
        weights = [head[1][j] for head in HEADS]
        draw_at = stream_end + 0.1 + (QUERY - 1 - j) * 0.08
        draw_total = draw_at + 0.6
        arcs.append(
            f'<path id="arc-{j}" d="M{qx:.1f} {arc_base:.1f} '
            f'Q{(qx + kx) / 2:.1f} {arc_base - 2 * apex:.1f} {kx:.1f} {arc_base:.1f}" '
            f'pathLength="1" stroke-dasharray="1" stroke-dashoffset="0" '
            f'stroke="{palette["ACCENT"]}" stroke-linecap="round" '
            f'stroke-width="{0.6 + 2.6 * weights[0]:.2f}" '
            f'stroke-opacity="{0.15 + 0.85 * weights[0]:.2f}">'
            f'<animate attributeName="stroke-dashoffset" values="1;1;0" '
            f'keyTimes="0;{_k(draw_at / draw_total)};1" dur="{_k(draw_total)}s" '
            f'fill="freeze"/>'
            f'<animate attributeName="stroke-opacity" '
            f'values="{_head_values([0.15 + 0.85 * w for w in weights])}" '
            f'keyTimes="{key_times}" dur="{_k(HEAD_CYCLE)}s" '
            f'begin="{_k(stream_end + 1.4)}s" repeatCount="indefinite"/>'
            f'<animate attributeName="stroke-width" '
            f'values="{_head_values([0.6 + 2.6 * w for w in weights])}" '
            f'keyTimes="{key_times}" dur="{_k(HEAD_CYCLE)}s" '
            f'begin="{_k(stream_end + 1.4)}s" repeatCount="indefinite"/>'
            f"</path>"
            f'<g><circle cx="{kx:.1f}" cy="{arc_base:.1f}" r="2" '
            f'fill="{palette["ACCENT"]}" fill-opacity="0.7"/>'
            f"{appear(draw_total - 0.1)}</g>"
        )
    arcs.append(
        f'<g><circle cx="{qx:.1f}" cy="{arc_base:.1f}" r="3" '
        f'fill="{palette["ACCENT"]}"/>{appear(stream_end)}</g>'
    )
    parts.append(f'<g id="attention">{"".join(arcs)}</g>')

    # Head label: one outline per head, only the active one visible.
    for h, (label, _) in enumerate(HEADS):
        mark, _ = mono_label(
            label, 11, 840, 76, palette["MUTED"], f"head-{h}", anchor_end=True
        )
        visible = [1.0 if i == h else 0.0 for i in range(len(HEADS))]
        parts.append(
            f'<g opacity="{1 if h == 0 else 0}">{mark}'
            f'<animate attributeName="opacity" values="{_head_values(visible)}" '
            f'keyTimes="{key_times}" dur="{_k(HEAD_CYCLE)}s" '
            f'begin="{_k(stream_end + 1.4)}s" repeatCount="indefinite" '
            f'calcMode="discrete"/>'
            f"</g>"
        )

    parts += chips

    # Caret rides the stream, then idles as a blinking cursor.
    stops = [spans[i][1] + 4 for i in range(len(HERO_TOKENS))]
    caret_values = [stops[0]] + stops
    caret_times = [0.0] + [
        (STREAM_START + i * STREAM_STEP) / stream_end for i in range(len(stops))
    ]
    parts.append(
        f'<rect id="caret" x="{stops[-1]:.1f}" y="{chip_top + 8:.1f}" width="3" '
        f'height="{chip_bottom - chip_top - 16:.1f}" fill="{palette["ACCENT"]}">'
        f'<animate attributeName="x" calcMode="discrete" '
        f'values="{";".join(f"{v:.1f}" for v in caret_values)}" '
        f'keyTimes="{";".join(_k(t) for t in caret_times)}" '
        f'dur="{_k(stream_end)}s" fill="freeze"/>'
        f'<animate attributeName="opacity" values="1;1;0;0" '
        f'keyTimes="0;0.5;0.5;1" dur="1.1s" begin="{_k(stream_end)}s" '
        f'repeatCount="indefinite"/>'
        f"</rect>"
    )

    gloss, _ = mono_label(
        "latency · evals · the bill · whether it still works on a Monday",
        14,
        40,
        chip_bottom + 46,
        palette["MUTED"],
        "gloss",
    )
    parts.append(f"<g>{gloss}{appear(stream_end + 0.2, fade=0.5)}</g>")

    rule_y = chip_bottom + 72
    parts.append(
        f'<path d="M40 {rule_y:.1f} H840" stroke="{palette["HAIRLINE"]}" '
        f'stroke-width="1"/>'
    )
    lede, last = outlined_block(
        regular,
        LEDE,
        19,
        40,
        rule_y + 38,
        palette["INK"],
        "lede",
        max_width=800,
        leading=28,
    )
    parts.append(lede)
    return _svg_doc(880, int(last + 22), "".join(parts))


# -------------------------------------------------------------------------- trace

# (span, tool, tree prefix, start, end, hue) on a 0..1 timeline.
SPANS: Final[tuple[tuple[str, str, str, float, float, str], ...]] = (
    ("request", "FastAPI · Docker", "", 0.00, 1.00, "T4"),
    ("agent.plan", "LangGraph", "├─ ", 0.02, 0.15, "T1"),
    ("retrieve.graph", "Neo4j", "├─ ", 0.15, 0.37, "T2"),
    ("retrieve.vector", "Milvus", "├─ ", 0.15, 0.30, "T2"),
    ("tool.call", "MCP", "├─ ", 0.37, 0.49, "T1"),
    ("generate", "Llama · LoRA", "├─ ", 0.49, 0.84, "T3"),
    ("serve", "Triton · TensorRT INT8", "│  └─ ", 0.50, 0.83, "T3"),
    ("eval", "LangSmith", "└─ ", 0.84, 0.97, "T5"),
)
ALSO: Final[str] = (
    "PyTorch · Transformers · FLUX · CrewAI · Pinecone · ONNX · MLflow · "
    "AWS · GCP · Azure"
)
TRACE_CYCLE: Final[float] = 10.0
SWEEP: Final[float] = 0.42  # fraction of the cycle the playhead takes to cross


def build_trace(palette: Theme) -> str:
    """The stack as a live distributed trace that replays every few seconds."""
    mono = plex_mono()
    left, right = 410.0, 840.0
    span_w = right - left
    parts: list[str] = []

    head, head_w = mono_label("TRACE", 13, 40, 34, palette["ACCENT"], "trace-head")
    sub, _ = mono_label(
        "one request through the stack I ship",
        13,
        40 + head_w + 14,
        34,
        palette["MUTED"],
        "trace-sub",
    )
    parts += [head, sub]

    # Status flips from running to passed when the playhead lands.
    run_label, run_w = mono_label(
        "running", 12, 840, 34, palette["MUTED"], "status-run", anchor_end=True
    )
    pass_label, _ = mono_label(
        "✓ evals passed", 12, 840, 34, palette["T3"], "status-pass", anchor_end=True
    )
    flip = _k(SWEEP)
    parts.append(
        f'<g opacity="0">{run_label}'
        f'<circle cx="{840 - run_w - 10:.1f}" cy="30" r="3" fill="{palette["MUTED"]}"/>'
        f'<animate attributeName="opacity" values="1;0" keyTimes="0;{flip}" '
        f'calcMode="discrete" dur="{_k(TRACE_CYCLE)}s" repeatCount="indefinite"/>'
        f"</g>"
        f"<g>{pass_label}"
        f'<animate attributeName="opacity" values="0;1" keyTimes="0;{flip}" '
        f'calcMode="discrete" dur="{_k(TRACE_CYCLE)}s" repeatCount="indefinite"/>'
        f"</g>"
    )

    axis_y = 60.0
    row0 = 92.0
    step = 28.0
    bottom = row0 + step * (len(SPANS) - 1) + 12
    grid = [f"M{left} {axis_y} H{right}"]
    for q in (0.0, 0.25, 0.5, 0.75, 1.0):
        gx = left + span_w * q
        grid.append(f"M{gx:.1f} {axis_y - 4} V{axis_y + 4}")
    parts.append(
        f'<path d="{" ".join(grid)}" stroke="{palette["HAIRLINE"]}" stroke-width="1"/>'
    )
    for q in (0.25, 0.5, 0.75):
        gx = left + span_w * q
        parts.append(
            f'<path d="M{gx:.1f} {axis_y + 8} V{bottom:.1f}" '
            f'stroke="{palette["HAIRLINE"]}" stroke-width="1" '
            f'stroke-dasharray="2 4"/>'
        )

    for i, (span, tool, prefix, start, end, hue) in enumerate(SPANS):
        y = row0 + step * i
        tree_w = text_width(mono, prefix, 13)
        if prefix:
            tree, _ = mono_label(prefix, 13, 40, y, palette["HAIRLINE"], f"tree-{i}")
            parts.append(tree)
        label, _ = mono_label(span, 13, 40 + tree_w, y, palette["INK"], f"span-{i}")
        tool_d, _ = mono_label(tool, 12, 236, y, palette["MUTED"], f"tool-{i}")
        bx = left + span_w * start
        bw = span_w * (end - start)
        t_start = max(start * SWEEP, 0.0005)
        t_end = end * SWEEP
        parts += [
            label,
            tool_d,
            f'<rect x="{bx:.1f}" y="{y - 10:.1f}" width="{bw:.1f}" height="12" '
            f'rx="3" fill="{palette[hue]}" fill-opacity="0.9">'
            f'<animate attributeName="width" '
            f'values="0;0;{bw:.1f};{bw:.1f}" '
            f'keyTimes="0;{_k(t_start)};{_k(t_end)};1" '
            f'dur="{_k(TRACE_CYCLE)}s" repeatCount="indefinite"/>'
            f"</rect>",
        ]

    parts.append(
        f'<g opacity="0">'
        f'<path d="M{left} {axis_y - 6} l-4 -6 h8 z" fill="{palette["ACCENT"]}"/>'
        f'<path d="M{left} {axis_y - 6} V{bottom:.1f}" '
        f'stroke="{palette["ACCENT"]}" stroke-width="1.5"/>'
        f'<animateTransform attributeName="transform" type="translate" '
        f'values="0 0;{span_w:.1f} 0;{span_w:.1f} 0" keyTimes="0;{flip};1" '
        f'dur="{_k(TRACE_CYCLE)}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="1;1;0;0" '
        f'keyTimes="0;{flip};{_k(SWEEP + 0.06)};1" '
        f'dur="{_k(TRACE_CYCLE)}s" repeatCount="indefinite"/>'
        f"</g>"
    )

    foot_y = bottom + 42
    parts.append(
        f'<path d="M40 {bottom + 18:.1f} H840" stroke="{palette["HAIRLINE"]}" '
        f'stroke-width="1"/>'
    )
    also, also_w = mono_label("ALSO", 11, 40, foot_y, palette["ACCENT"], "also")
    bench, _ = mono_label(
        ALSO, 12, 40 + also_w + 14, foot_y, palette["MUTED"], "also-list"
    )
    parts += [also, bench]
    return _svg_doc(880, int(foot_y + 16), "".join(parts))


# ----------------------------------------------------------------------- receipts

# (system, context, scale, before, after, headline, unit, footnote, hue)
# scale: "rel" draws before as 1.0 of half the track, "abs" as a percentage of
# the full track, "" draws no bar because there is no honest baseline to draw.
RECEIPTS: Final[tuple[tuple[str, str, str, float, float, str, str, str, str], ...]] = (
    (
        "catalog search",
        "semantic match + learn-to-rank · 5k QPS",
        "rel",
        1.0,
        1.5,
        "+50%",
        "click-through",
        "+10% revenue",
        "T1",
    ),
    (
        "roofs from the air",
        "line detection on aerial imagery",
        "abs",
        0.28,
        0.59,
        "28% → 59%",
        "",
        "facets at 86% mIoU",
        "T2",
    ),
    (
        "GPU serving",
        "Triton + TensorRT INT8",
        "rel",
        1.0,
        0.70,
        "−30%",
        "VRAM",
        "25% faster",
        "T3",
    ),
    (
        "KYC face stack",
        "face verification for onboarding",
        "rel",
        1.0,
        0.75,
        "~25%",
        "less manual review",
        "",
        "T4",
    ),
    (
        "OCR",
        "ICDAR 2013 · BERT correction pass",
        "",
        0.0,
        0.0,
        "+12%",
        "vs Google Vision",
        "at a tenth of the infra",
        "T5",
    ),
    (
        "assistant",
        "English + Hinglish · national scale",
        "",
        0.0,
        0.0,
        "1000s",
        "chats a day",
        "",
        "T1",
    ),
)


def build_receipts(palette: Theme) -> str:
    """Shipped numbers as before → after bars. Only numbers that were measured."""
    track_x, track_w = 330.0, 260.0
    delta_x = 614.0
    parts: list[str] = []

    head, head_w = mono_label("RECEIPTS", 13, 40, 34, palette["ACCENT"], "rc-head")
    sub, _ = mono_label(
        "from systems that shipped",
        13,
        40 + head_w + 14,
        34,
        palette["MUTED"],
        "rc-sub",
    )
    after_l, after_w = mono_label(
        "after", 11, 840, 34, palette["MUTED"], "lg-after", anchor_end=True
    )
    before_x = 840 - after_w - 14 - 18 - 12
    before_l, before_w = mono_label(
        "before", 11, before_x, 34, palette["MUTED"], "lg-before", anchor_end=True
    )
    parts += [
        head,
        sub,
        after_l,
        before_l,
        f'<rect x="{840 - after_w - 26:.1f}" y="25" width="18" height="9" rx="2" '
        f'fill="{palette["INK"]}" fill-opacity="0.75"/>',
        f'<rect x="{before_x - before_w - 26:.1f}" y="25.5" width="18" height="8" '
        f'rx="2" fill="none" stroke="{palette["MUTED"]}" stroke-dasharray="3 2"/>',
        f'<path d="M40 48 H840" stroke="{palette["HAIRLINE"]}" stroke-width="1"/>',
    ]

    y = 86.0
    step = 56.0
    for i, (name, context, scale, before, after, big, unit, note, hue) in enumerate(
        RECEIPTS
    ):
        color = palette[hue]
        label, _ = mono_label(name, 15, 40, y, palette["INK"], f"rc-name-{i}")
        ctx, _ = mono_label(context, 11, 40, y + 18, palette["MUTED"], f"rc-ctx-{i}")
        parts += [label, ctx]
        if scale:
            unit_w = track_w / 2 if scale == "rel" else track_w
            b_w = unit_w * before
            a_w = unit_w * after
            begin = 0.4 + i * 0.14
            total = begin + 1.1
            parts += [
                f'<rect x="{track_x}" y="{y - 12:.1f}" width="{track_w}" '
                f'height="14" rx="3" fill="{palette["HAIRLINE"]}" '
                f'fill-opacity="0.35"/>',
                f'<rect x="{track_x}" y="{y - 12:.1f}" width="{a_w:.1f}" height="14" '
                f'rx="3" fill="{color}">'
                f'<animate attributeName="width" '
                f'values="{b_w:.1f};{b_w:.1f};{a_w:.1f}" '
                f'keyTimes="0;{_k(begin / total)};1" '
                f'keySplines="0 0 1 1;0.2 0.8 0.2 1" '
                f'calcMode="spline" dur="{_k(total)}s" fill="freeze"/>'
                f"</rect>",
                f'<rect x="{track_x}" y="{y - 12:.1f}" width="{b_w:.1f}" height="14" '
                f'rx="3" fill="none" stroke="{palette["INK"]}" stroke-opacity="0.55" '
                f'stroke-width="1.2" stroke-dasharray="3 2"/>',
            ]
        big_d, big_w = mono_label(big, 20, delta_x, y + 1, color, f"rc-big-{i}")
        parts.append(big_d)
        if unit:
            unit_d, _ = mono_label(
                unit, 12, delta_x + big_w + 8, y, palette["INK"], f"rc-unit-{i}"
            )
            parts.append(unit_d)
        if note:
            note_d, _ = mono_label(
                note, 11, delta_x, y + 18, palette["MUTED"], f"rc-note-{i}"
            )
            parts.append(note_d)
        if i < len(RECEIPTS) - 1:
            parts.append(
                f'<path d="M40 {y + 32:.1f} H840" stroke="{palette["HAIRLINE"]}" '
                f'stroke-width="1" stroke-opacity="0.6"/>'
            )
        y += step
    return _svg_doc(880, int(y - step + 40), "".join(parts))


# --------------------------------------------------------------------------- dock

DOCK: Final[tuple[tuple[str, str, str], ...]] = (
    # (stem, label, value)
    ("dock-site", "STUDIO", "immovabletech.com"),
    ("dock-mail", "MAIL", "rishabpal.work@gmail.com"),
    ("dock-link", "LINKEDIN", "in/rishabpal"),
)


def build_dock(palette: Theme, index: int, label: str, value: str) -> str:
    """One third of the 880 grid; markdown owns the href.

    The README sets each key to 33.33% with no whitespace between them, so the
    three images tile one 880-wide row. Each key's frame is offset inside its
    tile so the row lines up with the 40..840 column of every other module.
    """
    tile = 880 / len(DOCK)
    gap = 20.0
    key_w = (800 - gap * (len(DOCK) - 1)) / len(DOCK)
    x0 = 40 + index * (key_w + gap) - index * tile
    height = 64
    tag, _ = mono_label(label, 10, x0 + 18, 26, palette["MUTED"], "dock-label")
    text, _ = mono_label(value, 14, x0 + 18, 47, palette["INK"], "dock-value")
    arrow, _ = mono_label(
        "↗",
        16,
        x0 + key_w - 16,
        32,
        palette["ACCENT"],
        "dock-arrow",
        anchor_end=True,
    )
    body = (
        f'<rect x="{x0 + 0.5:.2f}" y="0.5" width="{key_w - 1:.2f}" '
        f'height="{height - 1}" rx="10" stroke="{palette["HAIRLINE"]}" '
        f'stroke-width="1"/>'
        f"{tag}{text}{arrow}"
    )
    return _svg_doc(round(tile, 3), height, body)
