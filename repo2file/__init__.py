"""repo2file - Repository content dumper for LLMs."""

__version__ = "2.0.0"

from .models import FileEntry, FileContent, Result
from .config import Config

__all__ = [
    "FileEntry",
    "FileContent",
    "Result",
    "Config",
    "__version__",
]
