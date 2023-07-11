import pytest

from steamship import Block, Steamship
from steamship.agents.llms import OpenAI
from steamship.agents.llms.openai import ChatOpenAI


@pytest.mark.usefixtures("client")
def test_openai_llm(client: Steamship):
    llm = OpenAI(client=client, temperature=0)
    blocks = llm.complete(prompt="Why did the chicken cross the road?", stop="side.")

    assert len(blocks) == 1
    assert blocks[0].is_text()


@pytest.mark.usefixtures("client")
def test_openai_llm_model_selection(client: Steamship):
    llm = OpenAI(client=client, temperature=0, model_name="gpt-4")
    blocks = llm.complete(prompt="Why did the chicken cross the road?", stop="side.")

    assert len(blocks) == 1
    assert blocks[0].is_text()


@pytest.mark.usefixtures("client")
def test_openai_llm_model_max_tokens_static(client: Steamship):
    llm = OpenAI(client=client, temperature=0, max_tokens=1)
    blocks = llm.complete(prompt="Why did the chicken cross the road?")

    assert len(blocks) == 1
    assert blocks[0].is_text()
    assert len(blocks[0].text.split()) == 1


@pytest.mark.usefixtures("client")
def test_openai_llm_model_max_tokens_dynamic(client: Steamship):
    llm = OpenAI(client=client, temperature=0)
    blocks = llm.complete(prompt="Why did the chicken cross the road?", max_tokens=1)

    assert len(blocks) == 1
    assert blocks[0].is_text()
    assert len(blocks[0].text.split()) == 1


@pytest.mark.usefixtures("client")
def test_openai_llm_chat_model_max_tokens_dynamic(client: Steamship):
    llm = ChatOpenAI(client=client, temperature=0)
    blocks = llm.chat(
        messages=[Block(text="Why did the chicken cross the road?")], tools=[], max_tokens=1
    )

    assert len(blocks) == 1
    assert blocks[0].is_text()
    assert len(blocks[0].text.split()) == 1
