"""Tests for error handling and edge cases."""

from pathlib import Path
import pytest
from repo2file.scanner import Scanner
from repo2file.readers import TextReader
from repo2file.models import FileEntry


def test_scanner_path_not_found():
    scanner = Scanner(Path("/nonexistent/path"))
    with pytest.raises(FileNotFoundError):
        list(scanner.scan())


def test_scanner_not_a_directory(tmp_path: Path):
    file = tmp_path / "file.txt"
    file.write_text("hello")
    scanner = Scanner(file)
    with pytest.raises(NotADirectoryError):
        list(scanner.scan())


def test_reader_os_error(tmp_path: Path):
    file = tmp_path / "unreadable.txt"
    file.write_text("content")
    file.chmod(0o000)
    
    try:
        entry = FileEntry(
            path=Path("unreadable.txt"),
            absolute_path=file,
            size=7,
            is_binary=False,
            is_symlink=False,
        )
        reader = TextReader()
        content = reader.read(entry)
        assert content.error is not None
    finally:
        file.chmod(0o644)


def test_scanner_permission_error(tmp_path: Path):
    subdir = tmp_path / "restricted"
    subdir.mkdir()
    (subdir / "file.txt").write_text("content")
    subdir.chmod(0o000)
    
    try:
        scanner = Scanner(tmp_path)
        entries = list(scanner.scan())
        assert len(entries) == 0
    finally:
        subdir.chmod(0o755)
