import pytest
import requests

from steamship import File, Steamship


def use_pdf(pdf_url: str, client: Steamship) -> File:
    """Use the PDF Blockifier from Python to parse a PDF into a nicely formatted document of Blocks."""

    pdf_response = requests.get(pdf_url)
    pdf_file = File.create(client, content=pdf_response.content)

    pdf_blockifier = client.use_plugin(
        plugin_handle="pdf-blockifier",
        config={},
    )

    task = pdf_file.blockify(plugin_instance=pdf_blockifier.handle)

    task.wait()  # Wait for the conversion to complete.

    pdf_file = pdf_file.refresh()

    return pdf_file


@pytest.mark.usefixtures("client")
def test_use_pdf(client: Steamship):
    file = use_pdf("https://www.steamship.com/test/pdf-test.pdf", client)
    for block in file.blocks:
        # Note: Markdown-style semantic annotations are in the block.tags property.
        assert block.text
        print(block.text)
