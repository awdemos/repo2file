"""Tests for output serializers."""

import json
from pathlib import Path
from repo2file.models import FileEntry, FileContent
from repo2file.serializers import TextSerializer, JsonSerializer, MarkdownSerializer


def make_content(path: str, text: str = None, error: str = None, is_binary: bool = False):
    entry = FileEntry(
        path=Path(path),
        absolute_path=Path("/tmp") / path,
        size=100,
        is_binary=is_binary,
        is_symlink=False,
    )
    return FileContent(entry=entry, text=text, encoding="utf-8", error=error)


def test_text_serializer(tmp_path: Path):
    output = tmp_path / "output.txt"
    serializer = TextSerializer()
    
    contents = [
        make_content("hello.py", text="print('hello')"),
        make_content("binary.png", is_binary=True),
    ]
    
    serializer.write(iter(contents), output)
    
    assert output.exists()
    text = output.read_text()
    assert "hello.py" in text
    assert "print('hello')" in text
    assert "BINARY FILE" in text


def test_json_serializer(tmp_path: Path):
    output = tmp_path / "output.json"
    serializer = JsonSerializer()
    
    contents = [make_content("test.py", text="x = 1")]
    serializer.write(iter(contents), output)
    
    data = json.loads(output.read_text())
    assert len(data) == 1
    assert data[0]["path"] == "test.py"
    assert data[0]["content"] == "x = 1"


def test_markdown_serializer(tmp_path: Path):
    output = tmp_path / "output.md"
    serializer = MarkdownSerializer()
    
    contents = [make_content("test.py", text="x = 1")]
    serializer.write(iter(contents), output)
    
    text = output.read_text()
    assert "# Repository Dump" in text
    assert "test.py" in text
    assert "```python" in text
