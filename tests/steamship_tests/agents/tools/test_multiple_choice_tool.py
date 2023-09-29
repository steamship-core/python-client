import pytest

from steamship import Block, Steamship
from steamship.agents.llms import OpenAI
from steamship.agents.schema import AgentContext
from steamship.agents.tools.classification.multiple_choice_tool import MultipleChoiceTool
from steamship.agents.utils import with_llm

TESTS = [
    ("Pencil", "Other"),
    ("America", "Countries,USA"),
    ("Ham sandwich", "Food,Lunch"),
]


@pytest.mark.parametrize(("x", "gold"), TESTS)
@pytest.mark.usefixtures("client")
def test_multiple_choice_tool(client: Steamship, x, gold):
    """Tests that we can inspect the package and mixin routes"""
    tool = MultipleChoiceTool()
    context = with_llm(
        OpenAI(client=client),
        AgentContext.get_or_create(client=client, context_keys={"id": "test"}),
    )

    res = tool.run([Block(text=x)], context)
    assert len(res) == 1
    assert res[0].text == gold
