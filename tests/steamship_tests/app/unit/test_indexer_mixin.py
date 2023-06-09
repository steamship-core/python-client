import pytest

from steamship import Steamship
from steamship.agents.llms import OpenAI
from steamship.agents.schema import AgentContext
from steamship.agents.tools.question_answering import VectorSearchQATool
from steamship.agents.utils import with_llm
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

    tool = VectorSearchQATool()
    context = with_llm(
        OpenAI(client=client),
        AgentContext.get_or_create(client=client, context_keys={"id": "test"}),
    )
    res = tool.answer_question("Mario", context)
    assert len(res) == 1
    assert res[0].text  # Note we can't test for the exact value here since the LLM will weigh in.
