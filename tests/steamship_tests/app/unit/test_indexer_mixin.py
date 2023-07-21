import pytest

from steamship import Steamship
from steamship.invocable.mixins.indexer_mixin import IndexerMixin


@pytest.mark.usefixtures("client")
def test_indexer_mixin_and_qa_tool(client: Steamship):
    """Tests that we can inspect the package and mixin routes"""
    indexer = IndexerMixin(client)
    assert indexer.index_text("Mario was a very fun game.")
    res = indexer.search_index("Mario")
    assert res.items
    assert len(res.items) == 1
    item = res.items[0]
    assert item.tag.text == "Mario was a very fun game."
    assert item.tag.value == {}

    assert indexer.index_text("Sonic was also pretty good.", metadata={"sega": True})
    res = indexer.search_index("Sonic")
    assert res.items
    assert len(res.items) == 2
    item = res.items[0]
    assert item.tag.text == "Sonic was also pretty good."
    assert item.tag.value
    assert item.tag.value.get("sega", True)
