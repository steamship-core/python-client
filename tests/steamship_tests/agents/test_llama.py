import pytest

from steamship import Block, Steamship, SteamshipError
from steamship.agents.llms import Llama, LlamaChat
from steamship.agents.tools.text_generation.text_rewrite_tool import TextRewritingTool
from steamship.data.tags.tag_constants import RoleTag


@pytest.mark.usefixtures("client")
def test_replicate_llama_llm(client: Steamship):
    llm = Llama(client=client, temperature=0)
    blocks = llm.complete(prompt="Why did the chicken cross the road?", stop_sequences="side.")

    assert len(blocks) == 1
    assert blocks[0].is_text()
    assert blocks[0].text


# The model doesn't appear to be respecting the max-tokens request.
# TODO: It's unclear if this is a bug in the plugin or a bug in the model. We'll have to test to see.
#
# @pytest.mark.usefixtures("client")
# def test_replicate_llama_llm_model_max_tokens_static(client: Steamship):
#     llm = Llama(client=client, temperature=0, max_tokens=2)
#     blocks = llm.complete(prompt="Why did the chicken cross the road?")
#
#     assert len(blocks) == 1
#     assert blocks[0].is_text()
#
#     assert len(blocks[0].text.split()) == 1
#     assert blocks[0].text


# Error delivery seems to be failing due to non-serializability of ReplicateError
# steamship.base.error.SteamshipError: [ERROR - POST /generate] Object of type ReplicateError is not JSON serializable
# @pytest.mark.usefixtures("client")
# def test_replicate_llama_llm_error_delivery(client: Steamship):
#     llm = Llama(client=client, temperature=0)
#
#     # TODO: Once the serialization error is fixed, wrap this in a `with pytest.raises(ValueError):` that matches
#     # the appropriate error message
#     blocks = llm.complete(prompt="", stop_sequences="side.")


@pytest.mark.usefixtures("client")
def test_openai_llm_chat_model_max_tokens_dynamic(client: Steamship):
    llm = LlamaChat(client=client, temperature=0)

    input_block = Block(
        text="Why did the chicken cross the road?",
    )
    input_block.set_chat_role(RoleTag.ASSISTANT)

    blocks = llm.chat(messages=[input_block], tools=[], max_tokens=1)

    assert len(blocks) == 1
    assert blocks[0].is_text()

    # Make sure the response was coherent.
    assert "side" in blocks[0].text


@pytest.mark.usefixtures("client")
def test_openai_llm_chat_model_throws_if_tools(client: Steamship):
    llm = LlamaChat(client=client, temperature=0)

    input_block = Block(
        text="Why did the chicken cross the road?",
    )
    input_block.set_chat_role(RoleTag.ASSISTANT)

    with pytest.raises(SteamshipError):
        llm.chat(messages=[input_block], tools=[TextRewritingTool()], max_tokens=1)
