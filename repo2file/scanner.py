"""Filesystem scanning with safety checks."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator, Optional

from .models import FileEntry


BINARY_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svgz',
    '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv',
    '.zip', '.tar', '.gz', '.bz2', '.7z', '.rar',
    '.exe', '.dll', '.so', '.dylib', '.bin',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx',
    '.woff', '.woff2', '.ttf', '.eot', '.otf',
    '.class', '.pyc', '.pyo', '.o', '.a',
    '.db', '.sqlite', '.sqlite3',
    '.jar', '.war', '.ear',
    '.iso', '.img',
}

TEXT_EXTENSIONS = {
    '.py', '.js', '.ts', '.tsx', '.jsx', '.html', '.htm',
    '.css', '.scss', '.sass', '.less', '.json', '.xml',
    '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
    '.md', '.rst', '.txt', '.csv', '.tsv',
    '.sh', '.bash', '.zsh', '.fish', '.ps1',
    '.c', '.cpp', '.cc', '.h', '.hpp', '.java',
    '.go', '.rs', '.rb', '.php', '.pl', '.pm',
    '.swift', '.kt', '.scala', '.r', '.m',
    '.sql', '.lua', '.vim', '.el', '.clj',
    '.dockerfile', '.makefile', '.cmake',
    '.graphql', '.proto', '.thrift',
    '.env', '.gitignore', '.gitattributes',
}


def detect_binary(path: Path, sample_size: int = 8192) -> bool:
    """Detect if a file is binary using null-byte heuristic."""
    suffix = path.suffix.lower()
    if suffix in TEXT_EXTENSIONS:
        return False
    if suffix in BINARY_EXTENSIONS:
        return True
    
    try:
        with open(path, 'rb') as f:
            chunk = f.read(sample_size)
            return b'\x00' in chunk
    except (OSError, IOError):
        return True


class Scanner:
    """Scans a directory tree and yields FileEntry objects."""
    
    def __init__(
        self,
        root: Path,
        max_depth: Optional[int] = None,
        follow_symlinks: bool = False,
    ):
        self.root = root.resolve()
        self.max_depth = max_depth
        self.follow_symlinks = follow_symlinks
    
    def scan(self) -> Iterator[FileEntry]:
        """Yield FileEntry for each file under root."""
        if not self.root.exists():
            raise FileNotFoundError(f"Path not found: {self.root}")
        if not self.root.is_dir():
            raise NotADirectoryError(f"Not a directory: {self.root}")
        
        for dirpath, dirnames, filenames in os.walk(
            self.root,
            followlinks=self.follow_symlinks,
        ):
            current_dir = Path(dirpath)
            
            try:
                rel_dir = current_dir.relative_to(self.root)
                depth = len(rel_dir.parts) if str(rel_dir) != '.' else 0
            except ValueError:
                continue
            
            if self.max_depth is not None and depth >= self.max_depth:
                dirnames[:] = []
                continue
            
            dirnames[:] = [
                d for d in dirnames
                if (current_dir / d).is_dir() and os.access(current_dir / d, os.R_OK)
            ]
            
            for filename in filenames:
                full_path = current_dir / filename
                rel_path = full_path.relative_to(self.root)
                
                is_symlink = full_path.is_symlink()
                if is_symlink and not self.follow_symlinks:
                    yield FileEntry(
                        path=rel_path,
                        absolute_path=full_path,
                        size=0,
                        is_binary=False,
                        is_symlink=True,
                    )
                    continue
                
                try:
                    stat = full_path.stat()
                    is_binary = detect_binary(full_path)
                    yield FileEntry(
                        path=rel_path,
                        absolute_path=full_path,
                        size=stat.st_size,
                        is_binary=is_binary,
                        is_symlink=is_symlink,
                    )
                except (OSError, IOError) as e:
                    continue
