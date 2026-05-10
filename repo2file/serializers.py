"""Output serializers for different formats."""

from __future__ import annotations

import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Iterator, Protocol

from .models import FileContent


class Serializer(Protocol):
    """Protocol for output serializers."""
    
    def write(self, contents: Iterator[FileContent], output: Path) -> None:
        """Write contents to output file."""
        ...


def _atomic_write(output: Path):
    """Create a temporary file for atomic writes."""
    return tempfile.NamedTemporaryFile(
        mode='w',
        encoding='utf-8',
        delete=False,
        dir=output.parent,
        prefix=f'.{output.name}.',
        suffix='.tmp',
    )


class TextSerializer:
    """Human-readable text format (legacy-compatible)."""
    
    def write(self, contents: Iterator[FileContent], output: Path) -> None:
        output.parent.mkdir(parents=True, exist_ok=True)
        tmp = _atomic_write(output)
        try:
            tmp.write("Directory Structure:\n")
            tmp.write("-------------------\n")
            
            entries = []
            tmp.write("\nFile Contents:\n")
            tmp.write("--------------\n")
            
            for content in contents:
                entries.append(content.entry)
                tmp.write(f"\nFile: {content.entry.path}\n")
                tmp.write("-" * 50 + "\n")
                
                if content.error:
                    tmp.write(f"[ERROR: {content.error}]\n")
                elif content.text is None:
                    if content.entry.is_binary:
                        tmp.write(f"[BINARY FILE: {content.entry.size} bytes]\n")
                    else:
                        tmp.write("[EMPTY FILE]\n")
                else:
                    tmp.write(content.text)
                
                tmp.write("\n\n")
            
            tmp.close()
            Path(tmp.name).rename(output)
            
        except Exception:
            Path(tmp.name).unlink(missing_ok=True)
            raise


class JsonSerializer:
    """Machine-readable JSON format."""
    
    def write(self, contents: Iterator[FileContent], output: Path) -> None:
        output.parent.mkdir(parents=True, exist_ok=True)
        tmp = _atomic_write(output)
        try:
            tmp.write('[\n')
            first = True
            
            for content in contents:
                if not first:
                    tmp.write(',\n')
                first = False
                
                data = {
                    'path': str(content.entry.path),
                    'size': content.entry.size,
                    'is_binary': content.entry.is_binary,
                    'is_symlink': content.entry.is_symlink,
                    'encoding': content.encoding,
                }
                
                if content.error:
                    data['error'] = content.error
                    data['content'] = None
                elif content.text is None:
                    data['content'] = None
                else:
                    data['content'] = content.text
                
                json.dump(data, tmp, indent=2)
            
            tmp.write('\n]\n')
            tmp.close()
            Path(tmp.name).rename(output)
            
        except Exception:
            Path(tmp.name).unlink(missing_ok=True)
            raise


class MarkdownSerializer:
    """Markdown format with code blocks."""
    
    def write(self, contents: Iterator[FileContent], output: Path) -> None:
        output.parent.mkdir(parents=True, exist_ok=True)
        tmp = _atomic_write(output)
        try:
            tmp.write(f"# Repository Dump\n\n")
            tmp.write(f"Generated: {datetime.now().isoformat()}\n\n")
            
            for content in contents:
                tmp.write(f"## {content.entry.path}\n\n")
                
                if content.error:
                    tmp.write(f"> **Error:** {content.error}\n\n")
                elif content.text is None:
                    if content.entry.is_binary:
                        tmp.write(f"> **Binary file:** {content.entry.size} bytes\n\n")
                    else:
                        tmp.write("> **Empty file**\n\n")
                else:
                    suffix = content.entry.path.suffix
                    lang = self._extension_to_lang(suffix)
                    tmp.write(f"```{lang}\n")
                    tmp.write(content.text)
                    tmp.write("\n```\n\n")
            
            tmp.close()
            Path(tmp.name).rename(output)
            
        except Exception:
            Path(tmp.name).unlink(missing_ok=True)
            raise
    
    def _extension_to_lang(self, ext: str) -> str:
        mapping = {
            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
            '.tsx': 'tsx', '.jsx': 'jsx', '.html': 'html', '.css': 'css',
            '.scss': 'scss', '.json': 'json', '.yaml': 'yaml', '.yml': 'yaml',
            '.md': 'markdown', '.sh': 'bash', '.bash': 'bash',
            '.c': 'c', '.cpp': 'cpp', '.h': 'c', '.hpp': 'cpp',
            '.java': 'java', '.go': 'go', '.rs': 'rust', '.rb': 'ruby',
            '.php': 'php', '.swift': 'swift', '.kt': 'kotlin',
            '.sql': 'sql', '.xml': 'xml', '.toml': 'toml',
        }
        return mapping.get(ext.lower(), '')
