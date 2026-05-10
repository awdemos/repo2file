"""Pipeline orchestrator for repo2file."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Iterator
import sys

from .config import Config
from .models import FileContent, Result
from .scanner import Scanner
from .filters import (
    GitignoreFilter,
    ExtensionFilter,
    CompositeFilter,
    load_gitignore,
)
from .readers import TextReader
from .serializers import TextSerializer, JsonSerializer, MarkdownSerializer


SERIALIZER_MAP = {
    'text': TextSerializer,
    'json': JsonSerializer,
    'markdown': MarkdownSerializer,
}


class Engine:
    """Orchestrates the scan → filter → read → serialize pipeline."""
    
    def __init__(self, config: Config):
        self.config = config
    
    def run(self) -> Result:
        """Execute the full pipeline."""
        start_time = time.time()
        
        scanner = Scanner(
            self.config.path,
            max_depth=self.config.max_depth,
            follow_symlinks=self.config.follow_symlinks,
        )
        
        filters = []
        
        gitignore_patterns = load_gitignore(self.config.gitignore)
        if gitignore_patterns:
            filters.append(GitignoreFilter(self.config.path, gitignore_patterns))
        
        if self.config.include_patterns:
            filters.append(ExtensionFilter(self.config.include_patterns))
        
        if self.config.exclude_patterns:
            from .filters import PatternFilter
            filters.append(PatternFilter(self.config.exclude_patterns))
        
        filter_chain = CompositeFilter(filters) if filters else None
        
        reader = TextReader(max_size=self.config.max_file_size)
        serializer_class = SERIALIZER_MAP.get(self.config.format, TextSerializer)
        serializer = serializer_class()
        
        files_scanned = 0
        files_included = 0
        files_binary = 0
        files_error = 0
        total_size = 0
        
        def read_filtered() -> Iterator[FileContent]:
            nonlocal files_scanned, files_included, files_binary, files_error, total_size
            
            for entry in scanner.scan():
                files_scanned += 1
                total_size += entry.size
                
                if filter_chain and not filter_chain.accept(entry):
                    continue
                
                files_included += 1
                
                if entry.is_binary:
                    files_binary += 1
                
                content = reader.read(entry)
                if content.error:
                    files_error += 1
                
                yield content
        
        self.config.output.parent.mkdir(parents=True, exist_ok=True)
        serializer.write(read_filtered(), self.config.output)
        
        duration = time.time() - start_time
        
        if self.config.verbose:
            print(f"Scanned: {files_scanned} files", file=sys.stderr)
            print(f"Included: {files_included} files", file=sys.stderr)
            print(f"Binary: {files_binary} files", file=sys.stderr)
            print(f"Errors: {files_error} files", file=sys.stderr)
            print(f"Output: {self.config.output}", file=sys.stderr)
            print(f"Duration: {duration:.2f}s", file=sys.stderr)
        
        return Result(
            files_scanned=files_scanned,
            files_included=files_included,
            files_binary=files_binary,
            files_error=files_error,
            total_size=total_size,
            output_path=self.config.output,
            duration_seconds=duration,
        )
