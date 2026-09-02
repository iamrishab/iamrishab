"""Stamp content/now.yml into the now-light and now-dark SVGs only."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml
from loguru import logger

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.datum import DIST, ROOT, build_now, load_tokens

NOW_YML = ROOT / "content" / "now.yml"


def read_now_line(path: Path) -> str:
    """Load the focus line. Empty or missing payload fails closed."""
    if not path.is_file():
        raise FileNotFoundError(f"missing {path}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("now.yml must be a mapping with a line key")
    line = payload.get("line")
    if not isinstance(line, str) or not line.strip():
        raise ValueError("now.yml line is empty")
    return line.strip()


def render_now_pair(line: str) -> None:
    """Rewrite only the now SVGs so a failed run cannot blank the other art."""
    tokens = load_tokens()
    DIST.mkdir(parents=True, exist_ok=True)
    for theme_name, palette in tokens.items():
        target = DIST / f"now-{theme_name}.svg"
        target.write_text(build_now(palette, line), encoding="utf-8")
        logger.info("wrote {}", target)


def main() -> None:
    """Keep the last good now SVGs if the yaml is unusable."""
    try:
        line = read_now_line(NOW_YML)
    except (FileNotFoundError, ValueError) as error:
        logger.error("now.yml unusable; leaving dist now SVGs unchanged: {}", error)
        raise SystemExit(1) from error
    render_now_pair(line)


if __name__ == "__main__":
    main()
