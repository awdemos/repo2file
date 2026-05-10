"""Safe file reading with binary detection."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .models import FileEntry, FileContent


class TextReader:
    """Reads text files safely, skipping binary files."""
    
    def __init__(self, max_size: int = 10_000_000):
        self.max_size = max_size
    
    def read(self, entry: FileEntry) -> FileContent:
        """Read file content safely."""
        if entry.is_binary:
            return FileContent(
                entry=entry,
                text=None,
                encoding=None,
                error=None,
            )
        
        if entry.size > self.max_size:
            return FileContent(
                entry=entry,
                text=None,
                encoding=None,
                error=f"File exceeds max size ({entry.size} > {self.max_size} bytes)",
            )
        
        try:
            with open(entry.absolute_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return FileContent(
                entry=entry,
                text=text,
                encoding='utf-8',
                error=None,
            )
        except UnicodeDecodeError:
            try:
                with open(entry.absolute_path, 'r', encoding='latin-1') as f:
                    text = f.read()
                return FileContent(
                    entry=entry,
                    text=text,
                    encoding='latin-1',
                    error=None,
                )
            except (OSError, IOError) as e:
                return FileContent(
                    entry=entry,
                    text=None,
                    encoding=None,
                    error=f"Read error: {e}",
                )
        except (OSError, IOError) as e:
            return FileContent(
                entry=entry,
                text=None,
                encoding=None,
                error=f"Read error: {e}",
            )
