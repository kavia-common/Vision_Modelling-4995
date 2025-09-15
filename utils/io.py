from __future__ import annotations

import os
import tempfile
from pathlib import Path


_BASE_DIR: Path | None = None


def _base_dir() -> Path:
    """Resolve the project base directory (container root)."""
    global _BASE_DIR
    if _BASE_DIR is None:
        # utils/io.py -> utils -> base (Vision_Modelling-4995)
        _BASE_DIR = Path(__file__).resolve().parents[1]
    return _BASE_DIR


# PUBLIC_INTERFACE
def get_data_dir() -> Path:
    """Resolve the data directory path honoring the DATA_DIR environment variable.

    Returns:
        Path: Absolute path to the data directory.
    """
    env_dir = os.getenv("DATA_DIR")
    if env_dir:
        return Path(env_dir).resolve()
    return _base_dir() / "data"


# PUBLIC_INTERFACE
def safe_write_text(path: Path, text: str) -> None:
    """Atomically write text content to a file, creating parent directories if needed.

    Args:
        path (Path): Destination file path.
        text (str): Text content to write.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=str(path.parent), encoding="utf-8") as tmp:
        tmp.write(text)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)
