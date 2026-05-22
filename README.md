# obsidian-md-converter

Convert Obsidian vault markdown to **GitHub Flavored Markdown (GFM)** so notes render and link correctly on GitHub and in tools that index Git repositories (search bots, Copilot, Cursor, etc.).

Primary use case: maintain notes in Obsidian, then publish a GFM-compatible copy to a public doc repo such as [kubernetes-learner](https://github.com/proksid/kubernetes-learner).

## Why this exists

Obsidian plugins that export to GitHub often mishandle wikilinks—especially headings and aliases. This CLI walks a folder of `.md` files and rewrites links in a predictable, test-covered way.

**Example**

| Obsidian | GFM |
|----------|-----|
| `[[Page Name]]` | `[Page Name](Page%20Name.md)` |
| `[[Page Name\|Display]]` | `[Display](Page%20Name.md)` |
| `[[Page#Heading]]` | `[Page#Heading](Page.md#heading)` |
| `[[#Heading]]` | `[Heading](#heading)` |
| `![[image.png]]` | unchanged (embedded assets skipped for now) |

## Install

Requires Python 3.12+ and [uv](https://github.com/astral-sh/uv).

```bash
git clone git@github.com:proksid/obsidian-md-converter.git
cd obsidian-md-converter
uv venv
uv sync
uv run obsidian-md-converter --help
```

## Usage

```bash
obsidian-md-converter SOURCE [OPTIONS]
```

| Option | Short | Description |
|--------|-------|-------------|
| `SOURCE` | — | File or directory to process (required) |
| `--destination` | `-d` | Output directory; omit to modify files in place |
| `--converter` | `-c` | Converter name (see below) |
| `--max-concurrent` | `-j` | Max parallel file operations (default: `50`) |

### Converters

| Name | Description |
|------|-------------|
| `wikilink-to-gfm` | Rewrite `[[wikilinks]]` to GFM links |
| `sandbox` | No transformation (copy / in-place rewrite only) |

For publishing to GitHub, use **`wikilink-to-gfm`**.

### Examples

Convert a vault folder into an output tree (keeps subfolder layout):

```bash
uv run obsidian-md-converter /path/to/vault/kubernetes \
  -d /path/to/kubernetes-learner \
  -c wikilink-to-gfm
```

Convert in place inside a clone of the doc repo:

```bash
cd kubernetes-learner
uv run obsidian-md-converter . -c wikilink-to-gfm
```

Process a single note:

```bash
uv run obsidian-md-converter note.md -d ./out -c wikilink-to-gfm
```

## Workflow with kubernetes-learner

1. Edit notes in Obsidian (wikilinks, embeds, attachments).
2. Export or sync markdown into a local folder (e.g. vault `kubernetes/`).
3. Run this tool with `-c wikilink-to-gfm` and `-d` pointing at the **kubernetes-learner** repo (or run in place on that repo).
4. Commit and push the doc repo so GitHub and indexing tools see GFM links.

The doc repo should keep a short **README** as the landing page for humans and bots; the main study hub can stay as `Kubernetes.md` (see kubernetes-learner). This tool repo only documents the converter—not the CKAD content itself.

Sample fixtures used in tests: `test_data/src/kubernetes` → `test_data/dst/kubernetes`.

## Development

```bash
uv sync --group dev
uv run pytest tests/ -v
uv run ruff check src tests
```

## Limitations

- Only `*.md` files under `SOURCE` are processed.
- Embedded links `![[...]]` are not converted yet.
- Attachment paths and HTML `<img>` tags are left as in the source.
- Anchor slug rules follow a GitHub-like normalization (Unicode, spaces, punctuation); edge cases may differ slightly from GitHub’s renderer.

## License

See repository license (if applicable).
