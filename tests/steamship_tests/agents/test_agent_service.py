from typing import List

import pytest
from steamship_tests import SRC_PATH
from steamship_tests.utils.deployables import deploy_package

from steamship import Block, Steamship, SteamshipError
from steamship.agents.schema import Action, AgentContext


def _blocks_from_invoke(client: Steamship, potential_blocks) -> List[Block]:
    try:
        if isinstance(potential_blocks, list):
            return [Block(client=client, **raw) for raw in potential_blocks]
        else:
            return [Block(client=client, **potential_blocks)]
    except Exception as e:
        raise SteamshipError(f"Could not convert to blocks: {e}")


@pytest.mark.usefixtures("client")
def test_example_with_caching_service(client: Steamship):

    # TODO(dougreid): replace the example agent with fake/free/fast tools to minimize test time / costs?

    example_caching_agent_path = (
        SRC_PATH / "steamship" / "agents" / "examples" / "example_assistant_with_caching.py"
    )
    with deploy_package(client, example_caching_agent_path) as (_, _, caching_agent):
        context_id = "foo-test-caching"
        context_keys = {"id": context_id}

        # attempt without caching
        blocks_json = caching_agent.invoke("prompt", prompt="draw a cat", context_id=context_id)
        assert blocks_json
        blocks = _blocks_from_invoke(client, blocks_json)
        assert len(blocks) == 2
        assert "image" in blocks[0].text
        assert blocks[1].is_image()

        agent_context = AgentContext.get_or_create(
            client=client, context_keys=context_keys, use_llm_cache=True, use_action_cache=True
        )
        # just clear the cache to start fresh
        agent_context.llm_cache.clear()
        agent_context.action_cache.clear()

        fake_action = Action(tool="fake_tool", input=[Block(text="a cat")])
        agent_context.llm_cache.update(key=[Block(text="draw a cat")], value=fake_action)

        fake_output = [Block(text="psyche")]
        agent_context.action_cache.update(key=fake_action, value=fake_output)

        fake_finish_action = Action(
            tool="Agent-FinishAction", input=[], output=[Block(text="insert cat image here")]
        )
        agent_context.llm_cache.update(key=fake_output, value=fake_finish_action)

        # now attempt with the caching
        blocks_json = caching_agent.invoke("prompt", prompt="draw a cat", context_id=context_id)
        assert blocks_json
        blocks = _blocks_from_invoke(client, blocks_json)
        assert len(blocks) == 1
        assert "insert cat image here" == blocks[0].text
