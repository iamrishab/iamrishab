"""Compile every profile module into light and dark dist files."""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path

import yaml

# Allow `uv run scripts/compile_svgs.py` without installing a package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.datum import DIST, ROOT, Theme, build_now, write_themed
from scripts.page import DOCK, build_dock, build_hero, build_receipts, build_trace


def compile_all(now_line: str) -> None:
    """Write all themed dist SVGs and drop any file no module produces."""
    for stale in DIST.glob("*.svg"):
        stale.unlink()
    write_themed("hero", build_hero)
    write_themed("trace", build_trace)
    write_themed("receipts", build_receipts)
    write_themed("now", lambda palette: build_now(palette, now_line))
    for index, (stem, label, value) in enumerate(DOCK):
        write_themed(stem, _dock(index, label, value))


def _dock(index: int, label: str, value: str) -> Callable[[Theme], str]:
    """Bind one dock key so the loop does not close over a changing variable."""

    def build(palette: Theme) -> str:
        return build_dock(palette, index, label, value)

    return build


def main() -> None:
    """Entry point used by local builds."""
    payload = yaml.safe_load((ROOT / "content" / "now.yml").read_text(encoding="utf-8"))
    compile_all(str(payload["line"]))


if __name__ == "__main__":
    main()
