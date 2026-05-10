"""Tests for filesystem scanner."""

from pathlib import Path
from repo2file.scanner import Scanner, detect_binary


def test_detect_binary_with_null_bytes(tmp_path: Path):
    binary_file = tmp_path / "binary.bin"
    binary_file.write_bytes(b"Hello\x00World")
    assert detect_binary(binary_file) is True


def test_detect_binary_text_file(tmp_path: Path):
    text_file = tmp_path / "text.txt"
    text_file.write_text("Hello World")
    assert detect_binary(text_file) is False


def test_detect_binary_by_extension(tmp_path: Path):
    png_file = tmp_path / "image.png"
    png_file.write_text("not really a png")
    assert detect_binary(png_file) is True


def test_scanner_finds_files(simple_repo: Path):
    scanner = Scanner(simple_repo)
    entries = list(scanner.scan())
    paths = {str(e.path) for e in entries}
    
    assert "README.md" in paths
    assert "src/main.py" in paths
    assert "image.png" in paths


def test_scanner_detects_binary(simple_repo: Path):
    scanner = Scanner(simple_repo)
    entries = list(scanner.scan())
    
    png_entry = next(e for e in entries if str(e.path) == "image.png")
    assert png_entry.is_binary is True


def test_scanner_respects_max_depth(simple_repo: Path):
    scanner = Scanner(simple_repo, max_depth=1)
    entries = list(scanner.scan())
    paths = {str(e.path) for e in entries}
    
    assert "README.md" in paths
    assert "src/main.py" not in paths


def test_scanner_empty_directory(tmp_path: Path):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    scanner = Scanner(empty_dir)
    entries = list(scanner.scan())
    assert len(entries) == 0
