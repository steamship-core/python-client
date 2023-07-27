import pytest

from steamship import Steamship
from steamship.invocable.mixins.indexer_mixin import DEFAULT_EMBEDDING_INDEX_HANDLE, IndexerMixin


@pytest.mark.usefixtures("client")
def test_indexer_mixin_and_qa_tool(client: Steamship):
    """Tests that we can inspect the package and mixin routes"""

    input_text = "Mario was a very fun game."
    indexer = IndexerMixin(client)
    assert indexer.index_text(input_text)
    res = indexer.search_index("Mario")
    assert res.items
    assert len(res.items) == 1
    item = res.items[0]
    assert item.tag.text == input_text
    assert isinstance(item.tag.value, dict)
    assert "_index" in item.tag.value
    assert item.tag.value["_index"] == DEFAULT_EMBEDDING_INDEX_HANDLE

    assert "chunk" in item.tag.value
    assert item.tag.value["chunk"] == input_text

    input_text_2 = "Sonic was also pretty good."
    assert indexer.index_text(input_text_2, metadata={"sega": True})
    res = indexer.search_index("Sonic")
    assert res.items
    assert len(res.items) == 2
    item = res.items[0]
    assert item.tag.text == input_text_2
    assert item.tag.value
    assert item.tag.value.get("sega", True)
