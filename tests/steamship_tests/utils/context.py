import pytest

from steamship import Steamship
from steamship.agents.schema import AgentContext


@pytest.mark.usefixtures("client")
def test_same_context(client: Steamship):
    context1 = AgentContext.get_or_create(client=client, context_keys={"one": "one", "two": "two"})
    contextsame = AgentContext.get_or_create(
        client=client, context_keys={"one": "one", "two": "two"}
    )

    assert context1.id == contextsame.id


@pytest.mark.usefixtures("client")
def test_different_context(client: Steamship):
    context1 = AgentContext.get_or_create(client=client, context_keys={"one": "one", "two": "two"})
    contextdiff = AgentContext.get_or_create(
        client=client, context_keys={"one": "one", "two": "three"}
    )
    assert context1.id != contextdiff.id
