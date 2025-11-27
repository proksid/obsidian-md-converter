"""Converters for transforming markdown content."""

import re
import unicodedata
from urllib.parse import quote


async def wikilink_to_gfm(content: str) -> str:
    """
    Convert Obsidian wikilinks to GitHub Flavored Markdown (GFM) format.

    Converts:
    - [[Page Name]] -> [Page Name](Page%20Name.md)
    - [[Page Name|Display Text]] -> [Display Text](Page%20Name.md)
    - [[Page Name#Heading]] -> [Page Name#Heading](Page%20Name.md#heading)
    - [[Page Name#Heading|Display Text]] -> [Display Text](Page%20Name.md#heading)

    Args:
        content: Markdown content with Obsidian wikilinks

    Returns:
        Content with wikilinks converted to GFM format
    """
    # Pattern to match Obsidian wikilinks: [[...]] or [[...|...]]
    # Handles:
    # - [[Page Name]] -> [Page Name](Page%20Name.md)
    # - [[Page Name|Display Text]] -> [Display Text](Page%20Name.md)
    # - [[Page Name#Heading]] -> [Page Name#Heading](Page%20Name.md#heading)
    # - [[Page Name#Heading|Display Text]] -> [Display Text](Page%20Name.md#heading)
    # - [[#Heading]] -> [Heading](#heading)
    # - [[#Heading|Display Text]] -> [Display Text](#heading)
    # Negative lookbehind skips embedded content links like ![[image.png]]
    pattern = r"(?<!\!)\[\[([^\]]+)\]\]"

    def replace_wikilink(match: re.Match[str]) -> str:
        link_content = match.group(1)

        # Whole link case: [[page_part#anchor_text|display_text]] -> [link_text](url)
        # Split by | to get page and display text
        if "|" in link_content:
            page_part, display_text = link_content.split("|", 1)
            page_part = page_part.strip()
            display_text = display_text.strip()
        else:
            page_part = link_content.strip()
            display_text = None

        anchor_part = ""
        filename = ""
        anchor_text = ""

        # Split by # to get page name and anchor
        if page_part.startswith("#"):
            page_name = ""
            anchor_text = page_part[1:].strip()
            if anchor_text:
                anchor_part = f"#{_normalize_anchor(anchor_text)}"
        elif "#" in page_part:
            page_name, anchor = page_part.split("#", 1)
            page_name = page_name.strip()
            anchor_text = anchor.strip()
            if anchor_text:
                anchor_part = f"#{_normalize_anchor(anchor_text)}"
        else:
            page_name = page_part

        # Convert page name to URL-encoded filename (if provided)
        page_name_clean = page_name.strip()
        if page_name_clean:
            filename = quote(page_name_clean, safe="/")
            if not filename.lower().endswith(".md"):
                filename = f"{filename}.md"

        # Build the GFM link
        url = f"{filename}{anchor_part}"

        if display_text is not None:
            link_text = display_text
        elif page_part.startswith("#"):
            link_text = anchor_text or page_part.lstrip("#")
        else:
            link_text = link_content.strip()

        return f"[{link_text}]({url})"

    return re.sub(pattern, replace_wikilink, content)


def _normalize_anchor(anchor: str) -> str:
    """Normalize anchor names to GitHub-style anchors / slugs.

    Args:
        anchor: The anchor name to normalize

    Returns:
        The normalized anchor name

    Examples:
        "Heading With Spaces / and Special Characters"
            -> "heading-with-spaces--and-special-characters"
    """
    # Replace spaces with hyphens and convert to lowercase first
    # This preserves double hyphens where special characters will be removed
    anchor_normalized = re.sub(r"\s+", "-", anchor.strip().lower())

    # Normalize Unicode characters (NFD decomposition)
    # This separates base characters from diacritics (e.g., "é" -> "e" + "´")
    anchor_normalized = unicodedata.normalize("NFD", anchor_normalized)

    # Filter to keep only:
    # - Unicode letters (L* categories)
    # - Unicode numbers (N* categories)
    # - Hyphens
    anchor_normalized = "".join(
        c
        for c in anchor_normalized
        if unicodedata.category(c).startswith(("L", "N")) or c == "-"
    )

    return anchor_normalized
