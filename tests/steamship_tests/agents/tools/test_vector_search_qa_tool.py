import pytest

from steamship import DocTag, Steamship
from steamship.agents.llms import OpenAI
from steamship.agents.schema import AgentContext
from steamship.agents.tools.question_answering import VectorSearchQATool
from steamship.agents.utils import with_llm
from steamship.data import TagKind
from steamship.invocable.mixins.indexer_mixin import IndexerMixin


@pytest.mark.usefixtures("client")
def test_vector_search_qa_tool(client: Steamship):
    """Tests that we can inspect the package and mixin routes"""
    indexer = IndexerMixin(client)
    assert indexer.index_text("Mario was a very fun game.", metadata={"nintendo": True})

    tool = VectorSearchQATool()
    context = with_llm(
        OpenAI(client=client),
        AgentContext.get_or_create(client=client, context_keys={"id": "test"}),
    )
    res = tool.answer_question("What was Mario?", context)
    assert len(res) == 1
    assert "game" in res[0].text

    assert res[0].tags is not None
    sources_tag = None
    for tag in res[0].tags:
        if tag.kind == TagKind.DOCUMENT and tag.name == DocTag.SOURCE:
            sources_tag = tag

    assert sources_tag
    assert sources_tag.value

    assert sources_tag.value.get("sources") is not None
    sources = sources_tag.value.get("sources")
    assert len(sources) == 1

    # This is the metadata we passed in at the top
    assert sources[0].get("nintendo") is True
