"""Core data models for repo2file pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class FileEntry:
    """Represents a discovered file in the repository."""
    path: Path
    absolute_path: Path
    size: int
    is_binary: bool
    is_symlink: bool


@dataclass(frozen=True)
class FileContent:
    """Represents the content of a file after reading."""
    entry: FileEntry
    text: Optional[str]
    encoding: Optional[str]
    error: Optional[str]


@dataclass
class Result:
    """Result statistics from a pipeline run."""
    files_scanned: int = 0
    files_included: int = 0
    files_binary: int = 0
    files_error: int = 0
    total_size: int = 0
    output_path: Optional[Path] = None
    duration_seconds: float = 0.0
