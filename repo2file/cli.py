"""Command-line interface for repo2file."""

from __future__ import annotations

import sys
from typing import List, Optional

from .config import Config
from .engine import Engine


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point."""
    try:
        config = Config.from_args(args)
        engine = Engine(config)
        result = engine.run()
        return 0
    except KeyboardInterrupt:
        print("\nAborted.", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
