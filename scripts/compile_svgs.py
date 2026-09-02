"""Compile every Living Datum composition into light and dark dist files."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

# Allow `uv run scripts/compile_svgs.py` without installing a package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.datum import (
    ROOT,
    build_act,
    build_hero,
    build_now,
    build_sigil,
    build_stack,
    build_work,
    write_src_templates,
    write_themed,
)


def compile_all(now_line: str) -> None:
    """Write src templates and all themed dist SVGs, including a static now pair."""
    write_src_templates()
    write_themed("sigil", build_sigil)
    write_themed("hero", build_hero)
    write_themed("act", build_act)
    write_themed("work", build_work)
    write_themed("stack", build_stack)
    write_themed("now", lambda palette: build_now(palette, now_line))


def main() -> None:
    """Entry point used by local builds and the profile Action."""
    payload = yaml.safe_load((ROOT / "content" / "now.yml").read_text(encoding="utf-8"))
    compile_all(str(payload["line"]))


if __name__ == "__main__":
    main()
