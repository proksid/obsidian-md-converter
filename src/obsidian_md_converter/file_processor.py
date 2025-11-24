import asyncio
from collections.abc import Awaitable, Callable
from pathlib import Path

import aiofiles


async def process_files(
    source: Path,
    destination: Path | None = None,
    converter_func: Callable[[str], Awaitable[str]] | None = None,
    max_concurrent: int = 50,
) -> None:
    """
    Recursively process files from source asynchronously.

    Args:
        source: File or directory to process
        destination: Optional output directory (if None, replaces originals)
        converter_func: Async function to convert file content
        max_concurrent: Maximum number of concurrent file operations (default: 50)
    """
    if not source.exists():
        raise ValueError(f"Source does not exist: {source}")

    # Handle single file
    if source.is_file():
        if destination:
            destination.mkdir(parents=True, exist_ok=True)
            output_path = destination / source.name
        else:
            output_path = source

        await _process_single_file(source, output_path, converter_func)
        return

    # Handle directory recursively with concurrency limit
    if source.is_dir():
        semaphore = asyncio.Semaphore(max_concurrent)
        tasks = []
        for file_path in source.rglob("*.md"):
            if destination:
                relative_path = file_path.relative_to(source)
                output_path = destination / relative_path
                # Create parent directory before spawning task to avoid race condition
                output_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                output_path = file_path

            tasks.append(
                _process_single_file_with_semaphore(
                    semaphore, file_path, output_path, converter_func
                )
            )

        await asyncio.gather(*tasks)


async def _process_single_file_with_semaphore(
    semaphore: asyncio.Semaphore,
    input_path: Path,
    output_path: Path,
    converter_func: Callable[[str], Awaitable[str]] | None,
) -> None:
    """Process a single file with semaphore for concurrency control."""
    async with semaphore:
        await _process_single_file(input_path, output_path, converter_func)


async def _process_single_file(
    input_path: Path, output_path: Path, converter_func: Callable[[str], Awaitable[str]] | None
) -> None:
    """Process a single file asynchronously."""
    try:
        async with aiofiles.open(input_path, encoding="utf-8") as f:
            content = await f.read()

        if converter_func:
            converted = await converter_func(content)
        else:
            converted = content

        async with aiofiles.open(output_path, "w", encoding="utf-8") as f:
            await f.write(converted)
    except asyncio.CancelledError:
        # Let cancellation propagate without wrapping
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to process {input_path}: {e}") from e
