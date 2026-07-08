from __future__ import annotations

import sys

from .app import run


def main(argv: list[str] | None = None) -> int:
    return run(sys.argv if argv is None else argv)
