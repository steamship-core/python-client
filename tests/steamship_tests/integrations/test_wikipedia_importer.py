import pytest
import requests

from steamship import File, Steamship


def use_wikipedia(url: str, client: Steamship) -> File:
    """Use Wikipedia from Python to parse Wikipedia HTML into a nicely formatted document of Blocks."""

    article_response = requests.get(url)
    article_steamship = File.create(client, content=article_response.content)

    wikipedia = client.use_plugin(
        plugin_handle="wikipedia-blockifier",
        config={},
    )

    task = article_steamship.blockify(plugin_instance=wikipedia.handle)

    task.wait()  # Wait for the conversion to complete.

    article_steamship = article_steamship.refresh()

    return article_steamship


@pytest.mark.usefixtures("client")
def test_use_wikipedia(client: Steamship):
    file = use_wikipedia("https://en.wikipedia.org/wiki/Parsing", client)
    for block in file.blocks:
        # Note: Markdown-style semantic annotations are in the block.tags property.
        assert block.text
        print(block.text)
