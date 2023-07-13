import pytest

from steamship import Block, File, Steamship
from steamship.agents.functional import FunctionsBasedOutputParser
from steamship.agents.schema import AgentContext, FinishAction


@pytest.mark.usefixtures("client")
def test_output_block_ids_are_converted(client: Steamship):
    context = AgentContext()
    context.client = client
    block_id = File.create(client, blocks=[Block(text="test")]).blocks[0].id
    test_text = f"Here is an image of an anteater: Block({block_id})."

    output_formatter = FunctionsBasedOutputParser()
    result = output_formatter.parse(test_text, context)

    assert isinstance(result, FinishAction)
    assert len(result.output) == 2
    assert result.output[1].id == block_id
