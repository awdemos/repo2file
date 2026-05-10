"""Tests for file readers."""

from pathlib import Path
from repo2file.models import FileEntry
from repo2file.readers import TextReader


def make_entry(path: str, size: int = 100, is_binary: bool = False) -> FileEntry:
    return FileEntry(
        path=Path(path),
        absolute_path=Path(path),
        size=size,
        is_binary=is_binary,
        is_symlink=False,
    )


def test_read_text_file(tmp_path: Path):
    file = tmp_path / "test.txt"
    file.write_text("Hello World")
    
    reader = TextReader()
    content = reader.read(make_entry(str(file), size=file.stat().st_size))
    
    assert content.text == "Hello World"
    assert content.encoding == "utf-8"
    assert content.error is None


def test_skip_binary_file():
    entry = make_entry("image.png", is_binary=True)
    reader = TextReader()
    content = reader.read(entry)
    
    assert content.text is None
    assert content.error is None


def test_read_latin1_fallback(tmp_path: Path):
    file = tmp_path / "latin.txt"
    file.write_bytes(b"Hello \xe9 World")
    
    reader = TextReader()
    content = reader.read(make_entry(str(file), size=file.stat().st_size))
    
    assert content.text is not None
    assert content.encoding == "latin-1"


def test_respects_max_size(tmp_path: Path):
    file = tmp_path / "large.txt"
    file.write_text("x" * 1000)
    
    reader = TextReader(max_size=100)
    content = reader.read(make_entry(str(file), size=file.stat().st_size))
    
    assert content.text is None
    assert "exceeds max size" in content.error
