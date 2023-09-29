import pytest

from steamship import File, Steamship


def use_youtube_importer(youtube_url: str, client: Steamship) -> File:
    """Use the PDF Blockifier from Python to parse a PDF into a nicely formatted document of Blocks."""

    youtube_importer = client.use_plugin(
        plugin_handle="youtube-transcript-importer",
        config={},
    )

    task = File.create_with_plugin(client, plugin_instance=youtube_importer.handle, url=youtube_url)

    task.wait()  # Wait for the import to complete.

    youtube_file = task.output

    # We still have to blockify it! After import we just have bytes. Now we need to convert those bytes
    # into something like text or markdown.

    markdown_blockifier = client.use_plugin(plugin_handle="markdown-blockifier-default")
    youtube_file.blockify(plugin_instance=markdown_blockifier.handle).wait()

    youtube_file = youtube_file.refresh()

    return youtube_file


@pytest.mark.usefixtures("client")
def test_use_youtube_importer(client: Steamship):
    file = use_youtube_importer("https://www.youtube.com/watch?v=qTgPSKKjfVg", client)
    assert len(file.blocks)
    for block in file.blocks:
        # Note: Markdown-style semantic annotations are in the block.tags property.
        assert block.text
        print(block.text)
