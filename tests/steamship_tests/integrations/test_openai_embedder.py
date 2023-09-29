from typing import List, Optional

import pytest

from steamship import Steamship
from steamship.data import TagKind, TagValueKey


def use_openai_embedder(text: str, client: Steamship) -> Optional[List[float]]:
    """Use OpenAI's Embedder to turn text into an embedding vector."""
    sd = client.use_plugin(
        plugin_handle="openai-embedder",
        config={"model": "text-embedding-ada-002", "dimensionality": 1536},
    )

    task = sd.tag(doc=text)

    task.wait()  # Wait for the generation to complete.

    for tag in task.output.file.blocks[0].tags:
        if tag.kind == TagKind.EMBEDDING:
            return tag.value.get(TagValueKey.VECTOR_VALUE)

    return None


@pytest.mark.usefixtures("client")
def test_use_openai_embedder(client: Steamship):
    embedding = use_openai_embedder("Pizza", client)
    assert embedding
    assert len(embedding)
    print(f"Your embedding is: {embedding}")
