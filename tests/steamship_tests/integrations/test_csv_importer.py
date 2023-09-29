import pytest

from steamship import File, Steamship


def use_csv(csv_content: str, config: dict, client: Steamship) -> File:
    """Use the CSV Blockifier from Python to parse CSV into a nicely formatted document of Blocks annotated with Tags."""

    csv_file = File.create(client, content=csv_content)

    csv_blockifier = client.use_plugin(
        plugin_handle="csv-blockifier",
        config=config,
    )

    task = csv_file.blockify(plugin_instance=csv_blockifier.handle)

    task.wait()  # Wait for the conversion to complete.

    csv_file = csv_file.refresh()

    return csv_file


@pytest.mark.usefixtures("client")
def test_use_csv(client: Steamship):
    csv = """name,company
Ronald McDonald,McDonalds
Hamburgler,McDonalds
Wendy,Wendy's
Colonel Sanders,Kentucky Fried Chicken
"""
    config = {"text_column": "name", "tag_kind": "Company", "tag_columns": "company"}
    file = use_csv(csv, config, client)
    for block in file.blocks:
        # Note: Markdown-style semantic annotations are in the block.tags property.
        assert block.text
        print(block.text)
        for tag in block.tags:
            print(f"- {tag.kind}: {tag.name}")
