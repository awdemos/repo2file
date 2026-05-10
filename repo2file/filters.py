"""Filtering logic for repository files."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Protocol
import pathspec

from .models import FileEntry


class Filter(Protocol):
    """Protocol for file filters."""
    
    def accept(self, entry: FileEntry) -> bool:
        """Return True if file should be included."""
        ...


class GitignoreFilter:
    """Filter based on gitignore patterns using pathspec."""
    
    def __init__(self, root: Path, patterns: List[str]):
        self.root = root
        self.spec = pathspec.PathSpec.from_lines('gitignore', patterns)
    
    def accept(self, entry: FileEntry) -> bool:
        path_str = entry.path.as_posix()
        return not self.spec.match_file(path_str)


class ExtensionFilter:
    """Filter based on file extensions."""
    
    def __init__(self, extensions: List[str]):
        self.extensions = set()
        for ext in extensions:
            ext = ext.lower()
            if not ext.startswith('.'):
                ext = '.' + ext
            self.extensions.add(ext)
    
    def accept(self, entry: FileEntry) -> bool:
        return entry.path.suffix.lower() in self.extensions


class PatternFilter:
    """Filter based on glob patterns."""
    
    def __init__(self, patterns: List[str], exclude: bool = True):
        self.patterns = patterns
        self.exclude = exclude
    
    def accept(self, entry: FileEntry) -> bool:
        import fnmatch
        path_str = str(entry.path)
        matches = any(fnmatch.fnmatch(path_str, p) for p in self.patterns)
        return not matches if self.exclude else matches


class CompositeFilter:
    """Combines multiple filters with AND logic."""
    
    def __init__(self, filters: List[Filter]):
        self.filters = filters
    
    def accept(self, entry: FileEntry) -> bool:
        return all(f.accept(entry) for f in self.filters)


def load_gitignore(path: Optional[Path]) -> List[str]:
    """Load gitignore patterns from file."""
    if path is None or not path.exists():
        return []
    
    patterns = []
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.rstrip('\n\r')
            if line and not line.startswith('#'):
                patterns.append(line)
    
    return patterns
