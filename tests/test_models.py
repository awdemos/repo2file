"""Tests for data models."""

from pathlib import Path
from repo2file.models import FileEntry, FileContent, Result


def test_file_entry_creation():
    entry = FileEntry(
        path=Path("test.py"),
        absolute_path=Path("/tmp/test.py"),
        size=100,
        is_binary=False,
        is_symlink=False,
    )
    assert entry.path == Path("test.py")
    assert entry.size == 100
    assert not entry.is_binary


def test_file_content_creation():
    entry = FileEntry(
        path=Path("test.py"),
        absolute_path=Path("/tmp/test.py"),
        size=100,
        is_binary=False,
        is_symlink=False,
    )
    content = FileContent(
        entry=entry,
        text="print('hello')",
        encoding="utf-8",
        error=None,
    )
    assert content.text == "print('hello')"
    assert content.encoding == "utf-8"


def test_result_defaults():
    result = Result()
    assert result.files_scanned == 0
    assert result.files_included == 0
    assert result.duration_seconds == 0.0
