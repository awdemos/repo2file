"""Tests for filtering logic."""

from pathlib import Path
from repo2file.models import FileEntry
from repo2file.filters import (
    GitignoreFilter,
    ExtensionFilter,
    CompositeFilter,
    load_gitignore,
)


def make_entry(path: str) -> FileEntry:
    return FileEntry(
        path=Path(path),
        absolute_path=Path("/tmp") / path,
        size=100,
        is_binary=False,
        is_symlink=False,
    )


def test_gitignore_filter_excludes_patterns():
    filter = GitignoreFilter(Path("/tmp"), ["*.pyc", "__pycache__/"])
    
    assert filter.accept(make_entry("main.py")) is True
    assert filter.accept(make_entry("main.pyc")) is False
    assert filter.accept(make_entry("__pycache__/cache.py")) is False


def test_extension_filter():
    filter = ExtensionFilter([".py", ".js"])
    
    assert filter.accept(make_entry("main.py")) is True
    assert filter.accept(make_entry("main.js")) is True
    assert filter.accept(make_entry("main.txt")) is False


def test_extension_filter_normalizes_dots():
    filter = ExtensionFilter(["py", "js"])
    assert filter.accept(make_entry("main.py")) is True


def test_composite_filter_and_logic():
    gitignore = GitignoreFilter(Path("/tmp"), ["*.pyc"])
    ext = ExtensionFilter([".py"])
    composite = CompositeFilter([gitignore, ext])
    
    assert composite.accept(make_entry("main.py")) is True
    assert composite.accept(make_entry("main.pyc")) is False
    assert composite.accept(make_entry("main.js")) is False


def test_load_gitignore_from_file(tmp_path: Path):
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("*.pyc\n__pycache__/\n")
    
    patterns = load_gitignore(gitignore)
    assert "*.pyc" in patterns
    assert "__pycache__/" in patterns


def test_load_gitignore_skips_comments(tmp_path: Path):
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("# This is a comment\n*.pyc\n")
    
    patterns = load_gitignore(gitignore)
    assert "# This is a comment" not in patterns
    assert "*.pyc" in patterns


def test_load_gitignore_none_path():
    patterns = load_gitignore(None)
    assert patterns == []
