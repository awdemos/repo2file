"""Tests for CLI and config."""

from pathlib import Path
import pytest
from repo2file.cli import main
from repo2file.config import Config


def test_cli_runs_successfully(simple_repo: Path, tmp_path: Path):
    output = tmp_path / "out.txt"
    result = main([str(simple_repo), "-o", str(output)])
    assert result == 0
    assert output.exists()


def test_cli_invalid_path():
    result = main(["/nonexistent/path"])
    assert result == 1


def test_cli_keyboard_interrupt(simple_repo: Path, tmp_path: Path, monkeypatch):
    def raise_interrupt(*args, **kwargs):
        raise KeyboardInterrupt()
    
    monkeypatch.setattr(Config, "from_args", raise_interrupt)
    result = main([str(simple_repo)])
    assert result == 130


def test_config_from_args_minimal():
    config = Config.from_args(["/tmp"])
    assert config.path == Path("/tmp").resolve()
    assert config.output == Path("output.txt")
    assert config.format == "text"


def test_config_from_args_all_options(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    output = tmp_path / "out.json"
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("*.pyc\n")
    
    config = Config.from_args([
        str(repo),
        "-o", str(output),
        "-f", "json",
        "-i", ".py", "-i", ".js",
        "-e", "*.tmp",
        "-g", str(gitignore),
        "--max-file-size", "1000",
        "--max-depth", "3",
        "--follow-symlinks",
        "-v",
    ])
    
    assert config.path == repo.resolve()
    assert config.output == output
    assert config.format == "json"
    assert config.include_patterns == [".py", ".js"]
    assert config.exclude_patterns == ["*.tmp"]
    assert config.gitignore == gitignore
    assert config.max_file_size == 1000
    assert config.max_depth == 3
    assert config.follow_symlinks is True
    assert config.verbose is True


def test_config_auto_detect_gitignore(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    gitignore = repo / ".gitignore"
    gitignore.write_text("*.pyc\n")
    
    config = Config.from_args([str(repo)])
    assert config.gitignore == gitignore


def test_config_no_gitignore(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    
    config = Config.from_args([str(repo)])
    assert config.gitignore is None


def test_config_from_json_file(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    config_file = tmp_path / "config.json"
    config_file.write_text('{"max_file_size": 5000, "max_depth": 2}')
    
    config = Config.from_args([str(repo), "--config", str(config_file)])
    assert config.max_file_size == 5000
    assert config.max_depth == 2
