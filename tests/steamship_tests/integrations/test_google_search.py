from typing import Optional

import pytest

from steamship import Steamship
from steamship.data import TagValueKey


def use_google_search(query: str, client: Steamship) -> Optional[str]:
    """Use Google Search from Python to generate search snippets about a topic."""
    google_search = client.use_plugin(
        plugin_handle="serpapi-wrapper",
        config={},
    )

    task = google_search.tag(doc=query)
    task.wait()

    print(task.output)

    for tag in task.output.file.blocks[0].tags:
        if tag.kind == "search-result":
            return tag.value.get(TagValueKey.STRING_VALUE)

    return None


@pytest.mark.usefixtures("client")
def test_use_google_search(client: Steamship):
    result = use_google_search("Where was George Washington", client)
    assert result
    print(f"Who was George Washington: {result}")
