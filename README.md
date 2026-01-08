# Converter from Obsidian doc to GitHub-compatible Markdown files
1. Convert WikiLink links to GFM-compatible ones (the existing plugins do not work properly)  
    e.g. [[#1.1. Test control|Test control]] -> \[Test control](#11-test-control)

## Install
1. Fetch and install within virtual env
```bash
git clone git@github.com:proksid/obsidian-md-converter.git
cd obsidian-md-converter
uv venv
uv sync --no-editable
uv run obsidian-md-converter --help
```
2. Convert wikilinks in *.md files to the same location
```bash
uv run obsidian-md-converter -c wikilink-to-gfm src_dir
```