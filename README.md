# repo2file

Repository content dumper for LLM prompts and RAG systems.

> **Version 2.0** — Complete rewrite from a 132-line script into a modular, tested Python package.

## What's New

This release replaces the original monolithic script with a proper pipeline architecture:

| Before (v1) | After (v2) |
|-------------|------------|
| 132-line single script | 10 modular Python modules |
| Broken custom fnmatch gitignore | Full gitignore compliance via `pathspec` |
| Crashes on binary files | Safe binary detection (null-byte + extension heuristics) |
| Zero tests | 41 tests, 88% coverage |
| Memory-inefficient string building | Streaming output with atomic writes |
| Only text output | Text, JSON, and Markdown formats |

## Installation

```bash
pip install repo2file
```

Or from source:

```bash
git clone https://github.com/awdemos/repo2file.git
cd repo2file
pip install -e ".[dev]"
```

## Usage

### Basic

```bash
repo2file /path/to/your/repo
```

### With Options

```bash
repo2file /path/to/your/repo \
  -o output.txt \
  -f markdown \
  -i .py .js .ts \
  -e "*.test.*" \
  --max-depth 3 \
  -v
```

### CLI Reference

| Option | Description |
|--------|-------------|
| `path` | Directory to scan |
| `-o, --output` | Output file path (default: output.txt) |
| `-f, --format` | Output format: text, json, markdown |
| `-i, --include` | File extensions to include (e.g., .py .js) |
| `-e, --exclude` | Additional exclusion patterns |
| `-g, --gitignore` | Path to .gitignore file (auto-detected if omitted) |
| `--max-file-size` | Max file size in bytes (default: 10MB) |
| `--max-depth` | Maximum directory depth |
| `--follow-symlinks` | Follow symbolic links |
| `-v, --verbose` | Verbose output |
| `--config` | JSON config file for advanced options |

### Output Formats

**text** - Human-readable format with directory structure and file contents

**json** - Machine-readable JSON array with file metadata and content

**markdown** - Markdown with code blocks and syntax highlighting

## Features

- **Gitignore-compliant filtering** using pathspec library
- **Safe binary detection** - skips binary files without crashing
- **Multiple output formats** - text, JSON, markdown
- **Streaming output** - memory efficient for large repositories
- **Atomic writes** - output is written to temp file then renamed
- **Extension filtering** - include only specific file types
- **Depth limiting** - control how deep to scan
- **Symlink handling** - configurable symlink following

## Testing

```bash
pytest --cov=repo2file
```

## Architecture

```
repo2file/
├── repo2file/
│   ├── __init__.py       # Package exports
│   ├── __main__.py       # python -m repo2file
│   ├── cli.py            # Command-line interface
│   ├── config.py         # Configuration management
│   ├── engine.py         # Pipeline orchestrator
│   ├── scanner.py        # Filesystem traversal
│   ├── filters.py        # Gitignore + extension filtering
│   ├── readers.py        # Safe file reading
│   ├── serializers.py    # Output formatting
│   └── models.py         # Data models
└── tests/                # Test suite
```

Pipeline: Scanner → Filter → Reader → Serializer

## License

MIT
