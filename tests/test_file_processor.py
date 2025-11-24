"""Tests for async file processor."""

from pathlib import Path

import pytest

from src.obsidian_md_converter.file_processor import process_files


@pytest.fixture
def temp_dir(tmp_path):
    """Create temporary directory structure for testing."""
    # Create source directory with files
    source = tmp_path / "source"
    source.mkdir()

    (source / "file1.md").write_text("# Test 1")
    (source / "file2.md").write_text("# Test 2")

    # Create subdirectory
    subdir = source / "subdir"
    subdir.mkdir()
    (subdir / "file3.md").write_text("# Test 3")

    return tmp_path


async def dummy_converter(content: str) -> str:
    """Simple converter that uppercases content."""
    return content.upper()


@pytest.mark.asyncio
async def test_process_single_file(temp_dir):
    """Test processing a single file."""
    source_file = temp_dir / "source" / "file1.md"
    destination = temp_dir / "output"
    destination.mkdir()

    await process_files(source_file, destination, dummy_converter)

    output_file = destination / "file1.md"
    assert output_file.exists()
    assert output_file.read_text() == "# TEST 1"


@pytest.mark.asyncio
async def test_process_single_file_in_place(temp_dir):
    """Test processing a single file in-place (replaces original)."""
    source_file = temp_dir / "source" / "file1.md"
    original_content = source_file.read_text()

    await process_files(source_file, None, dummy_converter)

    assert source_file.read_text() == original_content.upper()


@pytest.mark.asyncio
async def test_process_directory_with_destination(temp_dir):
    """Test processing directory with destination (preserves hierarchy)."""
    source = temp_dir / "source"
    destination = temp_dir / "output"

    await process_files(source, destination, dummy_converter)

    assert (destination / "file1.md").exists()
    assert (destination / "file2.md").exists()
    assert (destination / "subdir" / "file3.md").exists()

    assert (destination / "file1.md").read_text() == "# TEST 1"
    assert (destination / "subdir" / "file3.md").read_text() == "# TEST 3"


@pytest.mark.asyncio
async def test_process_directory_in_place(temp_dir):
    """Test processing directory in-place (replaces originals)."""
    source = temp_dir / "source"
    original_content = (source / "file1.md").read_text()

    await process_files(source, None, dummy_converter)

    assert (source / "file1.md").read_text() == original_content.upper()
    assert (source / "file2.md").read_text() == "# TEST 2"


@pytest.mark.asyncio
async def test_process_without_converter(temp_dir):
    """Test processing without converter (copies files)."""
    source = temp_dir / "source" / "file1.md"
    destination = temp_dir / "output"
    destination.mkdir()

    await process_files(source, destination)

    output_file = destination / "file1.md"
    assert output_file.exists()
    assert output_file.read_text() == "# Test 1"


@pytest.mark.asyncio
async def test_nonexistent_source():
    """Test error handling for nonexistent source."""
    with pytest.raises(ValueError, match="Source does not exist"):
        await process_files(Path("/nonexistent/path"))


@pytest.mark.asyncio
async def test_empty_directory(temp_dir):
    """Test processing empty directory."""
    empty_dir = temp_dir / "empty"
    empty_dir.mkdir()
    destination = temp_dir / "output"

    await process_files(empty_dir, destination, dummy_converter)

    # Should complete without errors, no output files created
    assert not any(destination.glob("*.md")) if destination.exists() else True
