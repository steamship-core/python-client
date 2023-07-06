import pytest

from steamship import Block, Steamship
from steamship.agents.schema import Action, AgentContext
from steamship.agents.tools.search import SearchTool


@pytest.mark.usefixtures("client")
def test_context_persist_hydrate(client: Steamship):

    ctx = AgentContext.get_or_create(client=client, context_keys={"id": "test-foo"})

    ctx.chat_history.append_user_message("this is a test yo")
    ctx.completed_steps.append(
        Action(
            tool=SearchTool(),
            input=[Block(text="where's waldo?")],
            output=[Block(text="location unknown")],
        )
    )

    file_handle = ctx.persist_to_file(client=client)
    retrieved_ctx = AgentContext.hydrate_from_file(client=client, file_handle=file_handle)

    assert retrieved_ctx.chat_history.last_user_message.text == "this is a test yo"
    assert len(retrieved_ctx.completed_steps) == 1
