import pytest

from steamship import Steamship
from steamship.agents.examples.document_qa_agent import ExampleDocumentQAService


@pytest.mark.usefixtures("client")
def test_qa_agent_inits(client: Steamship):
    agent = ExampleDocumentQAService(client=client)
    assert agent is not None
