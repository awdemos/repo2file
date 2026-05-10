"""Shared test fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def simple_repo(tmp_path: Path) -> Path:
    """Create a simple repository with various file types."""
    repo = tmp_path / "simple_repo"
    repo.mkdir()
    
    (repo / "src").mkdir()
    (repo / "tests").mkdir()
    (repo / "docs").mkdir()
    
    (repo / "README.md").write_text("# Test Repo\n")
    (repo / "src" / "main.py").write_text("print('hello')\n")
    (repo / "src" / "utils.py").write_text("def helper():\n    pass\n")
    (repo / "tests" / "test_main.py").write_text("def test_main():\n    pass\n")
    (repo / "docs" / "guide.md").write_text("# Guide\n")
    (repo / "image.png").write_bytes(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
    (repo / "empty.txt").write_text("")
    (repo / ".gitignore").write_text("*.pyc\n__pycache__/\n")
    
    return repo


@pytest.fixture
def gitignore_repo(tmp_path: Path) -> Path:
    """Create a repo with complex gitignore patterns."""
    repo = tmp_path / "gitignore_repo"
    repo.mkdir()
    
    (repo / "keep.txt").write_text("keep\n")
    (repo / "ignore.tmp").write_text("ignore\n")
    (repo / "build").mkdir()
    (repo / "build" / "output.js").write_text("built\n")
    (repo / "src").mkdir()
    (repo / "src" / "main.py").write_text("main\n")
    (repo / "src" / "secret.key").write_text("secret\n")
    
    (repo / ".gitignore").write_text("""
# Build artifacts
/build/
*.tmp

# Secrets
*.key
""")
    
    return repo


@pytest.fixture
def binary_repo(tmp_path: Path) -> Path:
    """Create a repo with various binary files."""
    repo = tmp_path / "binary_repo"
    repo.mkdir()
    
    (repo / "ascii.txt").write_text("Hello World\n")
    (repo / "utf8.txt").write_text("Hello World\n")
    (repo / "null_bytes.bin").write_bytes(b"Hello\x00World")
    (repo / "image.jpg").write_bytes(b'\xff\xd8\xff\xe0' + b'\x00' * 100)
    
    return repo
