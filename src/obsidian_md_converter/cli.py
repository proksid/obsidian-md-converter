"""CLI entry point for obsidian-md-converter."""

import asyncio
from collections.abc import Awaitable, Callable
from pathlib import Path

import click

from . import __version__
from .converters import wikilink_to_gfm
from .file_processor import process_files

# Registry of available converters
CONVERTERS: dict[str, Callable[[str], Awaitable[str]]] = {
    "wikilink-to-gfm": wikilink_to_gfm,
    "sandbox": None,
}


@click.command()
@click.version_option(version=__version__)
@click.argument(
    "source",
    type=click.Path(exists=True, path_type=Path, file_okay=True, dir_okay=True),
    required=True,
)
@click.option(
    "--destination",
    "-d",
    type=click.Path(path_type=Path, file_okay=False, dir_okay=True),
    default=None,
    help="Output directory (if not specified, files are modified in-place)",
)
@click.option(
    "--converter",
    "-c",
    type=click.Choice(list(CONVERTERS.keys()), case_sensitive=False),
    default="sandbox",
    help="Converter function to use (default: sandbox)",
    show_default=True,
)
@click.option(
    "--max-concurrent",
    "-j",
    type=int,
    default=50,
    help="Maximum number of concurrent file operations",
    show_default=True,
)
def main(
    source: Path,
    destination: Path | None,
    converter: str,
    max_concurrent: int,
) -> None:
    """
    Convert Obsidian markdown files.

    Processes markdown files from SOURCE directory (or single file) and converts
    them using the specified converter function. If DESTINATION is not provided,
    files are modified in-place.
    """
    # Get the converter function
    converter_func = CONVERTERS.get(converter.lower())
    # if converter_func is None:
    #     click.echo(f"Error: Unknown converter '{converter}'", err=True)
    #     click.echo(f"Available converters: {', '.join(CONVERTERS.keys())}", err=True)
    #     raise click.Abort()

    # Run the async processing
    try:
        asyncio.run(
            process_files(
                source=source,
                destination=destination,
                converter_func=converter_func,
                max_concurrent=max_concurrent,
            )
        )
        click.echo("✓ Processing completed successfully")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e


if __name__ == "__main__":
    main()
