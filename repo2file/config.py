"""Configuration management for repo2file."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List


@dataclass
class Config:
    """Complete configuration for a repo2file run."""
    path: Path
    output: Path
    format: str = "text"
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    gitignore: Optional[Path] = None
    max_file_size: int = 10_000_000
    max_depth: Optional[int] = None
    follow_symlinks: bool = False
    verbose: bool = False

    @classmethod
    def from_args(cls, args: Optional[List[str]] = None) -> Config:
        """Create Config from command line arguments."""
        parser = argparse.ArgumentParser(
            prog="repo2file",
            description="Dump repository contents for LLM consumption",
        )
        parser.add_argument("path", type=Path, help="Directory to scan")
        parser.add_argument("-o", "--output", type=Path, default=Path("output.txt"),
                          help="Output file path (default: output.txt)")
        parser.add_argument("-f", "--format", choices=["text", "json", "markdown"],
                          default="text", help="Output format")
        parser.add_argument("-i", "--include", action="append", default=[],
                          help="File extensions to include (e.g., .py .js)")
        parser.add_argument("-e", "--exclude", action="append", default=[],
                          help="Additional exclusion patterns")
        parser.add_argument("-g", "--gitignore", type=Path,
                          help="Path to .gitignore file (auto-detected if omitted)")
        parser.add_argument("--max-file-size", type=int, default=10_000_000,
                          help="Max file size in bytes")
        parser.add_argument("--max-depth", type=int,
                          help="Maximum directory depth")
        parser.add_argument("--follow-symlinks", action="store_true",
                          help="Follow symbolic links")
        parser.add_argument("-v", "--verbose", action="store_true",
                          help="Verbose output")
        parser.add_argument("--config", type=Path,
                          help="JSON config file for advanced options")

        parsed = parser.parse_args(args)

        # Load config file if specified (overrides defaults but not explicit CLI args)
        if parsed.config and parsed.config.exists():
            with open(parsed.config) as f:
                file_config = json.load(f)
            # Get defaults from parser to know what was explicitly set vs defaulted
            defaults = {a.dest: a.default for a in parser._actions}
            for key, value in file_config.items():
                current = getattr(parsed, key, None)
                default = defaults.get(key)
                # Only override if user didn't explicitly set a different value
                if current == default or current is None:
                    setattr(parsed, key, value)

        # Auto-detect .gitignore
        gitignore_path = parsed.gitignore
        if gitignore_path is None:
            auto_gitignore = parsed.path / ".gitignore"
            if auto_gitignore.exists():
                gitignore_path = auto_gitignore

        return cls(
            path=parsed.path.resolve(),
            output=parsed.output,
            format=parsed.format,
            include_patterns=parsed.include,
            exclude_patterns=parsed.exclude,
            gitignore=gitignore_path,
            max_file_size=parsed.max_file_size,
            max_depth=parsed.max_depth,
            follow_symlinks=parsed.follow_symlinks,
            verbose=parsed.verbose,
        )
