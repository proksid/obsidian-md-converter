"""Obsidian Markdown Converter package."""

from importlib.metadata import PackageNotFoundError, version

# Try to get version from installed package metadata first
# Falls back to reading pyproject.toml if package is not installed
try:
    __version__ = version("obsidian-md-converter")
except PackageNotFoundError:
    # Fallback: read from pyproject.toml (for development/editable installs)
    from pathlib import Path
    from tomllib import load

    _pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    try:
        with _pyproject_path.open("rb") as f:
            _pyproject_data = load(f)
            __version__ = _pyproject_data["project"]["version"]
    except (FileNotFoundError, KeyError) as e:
        raise RuntimeError(
            f"Could not read version from package metadata or pyproject.toml: {e}"
        ) from e

__all__ = ["__version__"]
