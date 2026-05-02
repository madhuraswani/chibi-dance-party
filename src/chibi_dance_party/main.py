from __future__ import annotations

import sys
from pathlib import Path

from .app import run_app


def main() -> int:
    base_dir = Path.cwd()
    return run_app(base_dir)


if __name__ == "__main__":
    sys.exit(main())
