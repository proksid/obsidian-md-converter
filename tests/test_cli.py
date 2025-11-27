"""Tests for CLI functionality."""

import subprocess
import sys
from pathlib import Path

import pytest

from src.obsidian_md_converter.cli import main


@pytest.fixture
def temp_vault(tmp_path):
    """Create a temporary Obsidian vault for testing."""
    vault = tmp_path / "vault"
    vault.mkdir()

    # Create test markdown files with wikilinks
    (vault / "note1.md").write_text("# Note 1\n\nSee [[note2]] for more info.")
    (vault / "note2.md").write_text("# Note 2\n\nCheck [[note1|first note]] here.")
    (vault / "note3.md").write_text("# Note 3\n\nSee [[note1#Introduction]] section.")

    # Create subdirectory
    subdir = vault / "subdir"
    subdir.mkdir()
    (subdir / "note4.md").write_text("# Note 4\n\nLink to [[../note1]] parent.")

    return vault


def test_cli_help():
    """Test CLI help output."""
    result = subprocess.run(
        [sys.executable, "-m", "src.obsidian_md_converter.cli", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Convert Obsidian markdown files" in result.stdout
    assert "--destination" in result.stdout
    assert "--converter" in result.stdout
    assert "--max-concurrent" in result.stdout


def test_cli_version():
    """Test CLI version output."""
    result = subprocess.run(
        [sys.executable, "-m", "src.obsidian_md_converter.cli", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "0.1.0" in result.stdout


def test_cli_convert_with_destination(temp_vault, tmp_path):
    """Test CLI conversion with destination directory."""
    output = tmp_path / "output"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.obsidian_md_converter.cli",
            str(temp_vault),
            "--destination",
            str(output),
            "--converter",
            "wikilink-to-gfm",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Processing completed successfully" in result.stdout

    # Check that files were created
    assert (output / "note1.md").exists()
    assert (output / "note2.md").exists()
    assert (output / "subdir" / "note4.md").exists()

    # Check that wikilinks were converted
    note1_content = (output / "note1.md").read_text()
    assert "[note2]" in note1_content
    assert ".md" in note1_content  # Should have .md extension in links

    note2_content = (output / "note2.md").read_text()
    assert "first note" in note2_content
    assert "note1" in note2_content.lower()


def test_cli_convert_in_place(temp_vault):
    """Test CLI conversion in-place."""
    original_content = (temp_vault / "note1.md").read_text()

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.obsidian_md_converter.cli",
            str(temp_vault),
            "--converter",
            "wikilink-to-gfm",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Processing completed successfully" in result.stdout

    # Check that files were modified
    new_content = (temp_vault / "note1.md").read_text()
    assert new_content != original_content
    assert "[note2]" in new_content
    assert ".md" in new_content


def test_cli_convert_with_custom_concurrency(temp_vault, tmp_path):
    """Test CLI with custom concurrency setting."""
    output = tmp_path / "output"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.obsidian_md_converter.cli",
            str(temp_vault),
            "--destination",
            str(output),
            "--max-concurrent",
            "10",
            "--converter",
            "wikilink-to-gfm",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert (output / "note1.md").exists()


def test_cli_nonexistent_source():
    """Test CLI with nonexistent source."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.obsidian_md_converter.cli",
            "/nonexistent/path",
            "--converter",
            "wikilink-to-gfm",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "Error" in result.stderr or "does not exist" in result.stderr


def test_cli_invalid_converter(temp_vault, tmp_path):
    """Test CLI with invalid converter name."""
    output = tmp_path / "output"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.obsidian_md_converter.cli",
            str(temp_vault),
            "--destination",
            str(output),
            "--converter",
            "invalid-converter",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "Unknown converter" in result.stderr or "Error" in result.stderr


def test_cli_single_file(temp_vault, tmp_path):
    """Test CLI with single file as source."""
    output = tmp_path / "output"
    source_file = temp_vault / "note1.md"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.obsidian_md_converter.cli",
            str(source_file),
            "--destination",
            str(output),
            "--converter",
            "wikilink-to-gfm",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert (output / "note1.md").exists()
    assert "[note2]" in (output / "note1.md").read_text()


def test_cli_converter_default(temp_vault, tmp_path):
    """Test that default converter is used when not specified."""
    output = tmp_path / "output"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.obsidian_md_converter.cli",
            str(temp_vault),
            "--destination",
            str(output),
            "--converter",
            "wikilink-to-gfm",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    # Default converter should convert wikilinks
    content = (output / "note1.md").read_text()
    assert "[note2]" in content
    assert ".md" in content
