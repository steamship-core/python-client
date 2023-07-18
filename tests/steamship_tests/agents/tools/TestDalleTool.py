import pytest
import requests

from steamship import Block, Steamship
from steamship.agents.llms import OpenAI
from steamship.agents.schema import AgentContext
from steamship.agents.tools.image_generation import DalleTool
from steamship.agents.utils import with_llm


@pytest.mark.usefixtures("client")
def test_dalle_tool(client: Steamship):
    """Tests that we can inspect the package and mixin routes"""
    tool = DalleTool()
    context = with_llm(
        OpenAI(client=client),
        AgentContext.get_or_create(client=client, context_keys={"id": "test"}),
    )
    res = tool.run([Block(text="Mario jumping over a fire flower")], context)
    assert len(res) == 1
    assert res[0].public_data is True

    # Test that we can get the public data
    block_url = f"{client.config.api_base}block/{res[0].id}/raw"
    data = requests.get(block_url, json={"id": res[0].id})
    assert data.ok is True
    assert data.content is not None


@pytest.mark.usefixtures("client")
def test_dalle_tool_private_block(client: Steamship):
    tool = DalleTool(make_output_public=False)
    context = with_llm(
        OpenAI(client=client),
        AgentContext.get_or_create(client=client, context_keys={"id": "test"}),
    )
    res = tool.run([Block(text="Mario jumping over a fire flower")], context)
    assert len(res) == 1
    assert res[0].public_data is False
