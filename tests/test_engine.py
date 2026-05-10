"""Integration tests for the pipeline engine."""

from pathlib import Path
from repo2file.config import Config
from repo2file.engine import Engine


def test_engine_text_output(simple_repo: Path, tmp_path: Path):
    config = Config(
        path=simple_repo,
        output=tmp_path / "output.txt",
        format="text",
    )
    
    engine = Engine(config)
    result = engine.run()
    
    assert result.files_scanned >= 5
    assert result.files_included >= 5
    assert result.output_path.exists()
    
    text = result.output_path.read_text()
    assert "README.md" in text
    assert "main.py" in text


def test_engine_json_output(simple_repo: Path, tmp_path: Path):
    config = Config(
        path=simple_repo,
        output=tmp_path / "output.json",
        format="json",
    )
    
    engine = Engine(config)
    result = engine.run()
    
    assert result.output_path.exists()
    import json
    data = json.loads(result.output_path.read_text())
    assert len(data) >= 5


def test_engine_respects_gitignore(gitignore_repo: Path, tmp_path: Path):
    config = Config(
        path=gitignore_repo,
        output=tmp_path / "output.txt",
        format="text",
        gitignore=gitignore_repo / ".gitignore",
    )
    
    engine = Engine(config)
    result = engine.run()
    
    text = result.output_path.read_text()
    assert "keep.txt" in text
    assert "ignore.tmp" not in text
    assert "secret.key" not in text


def test_engine_with_extensions(simple_repo: Path, tmp_path: Path):
    config = Config(
        path=simple_repo,
        output=tmp_path / "output.txt",
        format="text",
        include_patterns=[".py"],
    )
    
    engine = Engine(config)
    result = engine.run()
    
    text = result.output_path.read_text()
    assert "main.py" in text
    assert "README.md" not in text


def test_engine_binary_safety(binary_repo: Path, tmp_path: Path):
    config = Config(
        path=binary_repo,
        output=tmp_path / "output.txt",
        format="text",
    )
    
    engine = Engine(config)
    result = engine.run()
    
    text = result.output_path.read_text()
    assert "ascii.txt" in text
    assert "null_bytes.bin" in text
    assert "BINARY FILE" in text
