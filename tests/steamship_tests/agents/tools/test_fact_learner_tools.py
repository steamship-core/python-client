import pytest
from steamship_tests import SRC_PATH
from steamship_tests.utils.deployables import deploy_package

from steamship import Block, Steamship


@pytest.mark.usefixtures("client")
def test_fact_learner_agent_service(client: Steamship):

    agent_path = SRC_PATH / "steamship/agents/examples/fact_learner.py"
    with deploy_package(client, agent_path) as (_, _, instance):

        instance.invoke("prompt", prompt="please remember that my name is Inigo Montoya")
        instance.invoke("prompt", prompt="please remember that I am skilled swordsman")

        answer_blocks = instance.invoke("prompt", prompt="what is my name?")
        assert len(answer_blocks) == 1
        assert "Inigo Montoya" in Block(**answer_blocks[0]).text

        answer_blocks = instance.invoke("prompt", prompt="what do I know how to do well?")
        assert len(answer_blocks) == 1
        assert "sword" in Block(**answer_blocks[0]).text
