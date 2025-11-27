"""Tests for markdown converters."""

import asyncio

import pytest

from src.obsidian_md_converter.converters import wikilink_to_gfm


@pytest.mark.asyncio
async def test_wikilink_simple():
    """Test simple wikilink conversion."""
    content = "This is a [[Page Name]] link."
    result = await wikilink_to_gfm(content)
    assert result == "This is a [Page Name](Page%20Name.md) link."


@pytest.mark.asyncio
async def test_wikilink_with_display_text():
    """Test wikilink with display text."""
    content = "Click [[Page Name|here]] to see more."
    result = await wikilink_to_gfm(content)
    assert result == "Click [here](Page%20Name.md) to see more."


@pytest.mark.asyncio
async def test_wikilink_with_anchor():
    """Test wikilink with anchor."""
    content = "See [[Page#Heading]] for details."
    result = await wikilink_to_gfm(content)
    assert result == "See [Page#Heading](Page.md#heading) for details."


@pytest.mark.asyncio
async def test_wikilink_with_anchor_and_display():
    """Test wikilink with anchor and display text."""
    content = "Check [[Page#Heading|this section]]."
    result = await wikilink_to_gfm(content)
    assert result == "Check [this section](Page.md#heading)."


@pytest.mark.asyncio
async def test_wikilink_multiple_links():
    """Test multiple wikilinks in one string."""
    content = "[[First]] and [[Second|another]] and [[Third#Anchor|third]]."
    result = await wikilink_to_gfm(content)
    assert (
        result
        == "[First](First.md) and [another](Second.md) and [third](Third.md#anchor)."
    )


@pytest.mark.asyncio
async def test_wikilink_with_spaces():
    """Test wikilink with spaces in page name."""
    content = "Link to [[My Page Name]] here."
    result = await wikilink_to_gfm(content)
    # Should URL-encode spaces
    assert "%20" in result or "My%20Page%20Name" in result
    assert "My Page Name" in result  # Display text should have spaces


@pytest.mark.asyncio
async def test_wikilink_complex_anchor():
    """Test wikilink with complex anchor."""
    content = "See [[Page#Heading With Spaces / and Spécial Characters]]."
    result = await wikilink_to_gfm(content)
    # Anchor should be lowercased and spaces converted to hyphens
    expected = (
        "[Page#Heading With Spaces / and Spécial Characters]"
        "(Page.md#heading-with-spaces--and-special-characters)"
    )
    assert expected in result


@pytest.mark.asyncio
async def test_wikilink_heading_only():
    """Test wikilinks that reference only a heading in the current file."""
    content = "Jump to [[#My Heading]] section."
    result = await wikilink_to_gfm(content)
    assert result == "Jump to [My Heading](#my-heading) section."


@pytest.mark.asyncio
async def test_wikilink_heading_with_display():
    """Test heading-only wikilink with display text."""
    content = "Jump to [[#My Heading|this part]]."
    result = await wikilink_to_gfm(content)
    assert result == "Jump to [this part](#my-heading)."


@pytest.mark.asyncio
async def test_wikilink_no_links():
    """Test content with no wikilinks."""
    content = "This is just regular text with no links."
    result = await wikilink_to_gfm(content)
    assert result == content


@pytest.mark.asyncio
async def test_wikilink_empty_content():
    """Test empty content."""
    content = ""
    result = await wikilink_to_gfm(content)
    assert result == ""


@pytest.mark.asyncio
async def test_wikilink_multiline():
    """Test wikilinks in multiline content."""
    content = """First paragraph with [[Link1]].

Second paragraph with [[Link2|display text]].

Third paragraph with [[Link3#Anchor]]."""
    result = await wikilink_to_gfm(content)
    assert "Link1" in result
    assert "display text" in result
    assert "Link3#Anchor" in result
    assert "#anchor" in result.lower()


@pytest.mark.asyncio
async def test_wikilink_special_characters():
    """Test wikilinks with special characters."""
    content = "Link to [[Page-Name_123]] here."
    result = await wikilink_to_gfm(content)
    # Special chars should be preserved or URL-encoded appropriately
    assert "Page-Name_123" in result or "Page%2DName_123" in result


@pytest.mark.asyncio
async def test_wikilink_nested_brackets():
    """Test that nested brackets don't break the regex."""
    content = "Text with [[Link]] and [regular markdown link](url)."
    result = await wikilink_to_gfm(content)
    # Should convert wikilink but preserve regular markdown link
    assert "[regular markdown link](url)" in result
    assert "Link" in result


@pytest.mark.asyncio
async def test_wikilink_embedded_is_ignored():
    """Ensure embedded content links (![[...]]) are left untouched."""
    content = "Image ![[diagram.png]] and link [[Page]]."
    result = await wikilink_to_gfm(content)
    assert "![[diagram.png]]" in result  # Embedded reference unchanged
    assert "[Page](Page.md)" in result


@pytest.mark.asyncio
async def test_wikilink_relative_path():
    """Test wikilink that references a relative path."""
    content = "See [[../folder/note]]."
    result = await wikilink_to_gfm(content)
    assert result == "See [../folder/note](../folder/note.md)."
