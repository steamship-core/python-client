import pytest

from steamship import Block, File, MimeTypes, Steamship
from steamship.agents.schema import Action
from steamship.agents.schema.cache import ActionCache, LLMCache


@pytest.mark.usefixtures("client")
def test_llm_cache(client: Steamship):
    context_keys = {"id": "test"}
    cache = LLMCache.get_or_create(client=client, context_keys=context_keys)

    key = [Block(text="prompt")]
    assert not cache.lookup(key)

    cache.update(key=key, value=Action(tool="example_tool", input=[Block(text="input")]))
    action = cache.lookup(key)
    assert action
    assert action.tool == "example_tool"
    assert action.input[0].text == "input"

    cache.update(key=key, value=Action(tool="example_tool", input=[Block(text="other")]))
    action = cache.lookup(key)
    assert action
    assert action.tool == "example_tool"
    assert action.input[0].text == "other"

    cache.delete(key)
    assert not cache.lookup(key)

    file = File.create(client=client, handle="whocares")
    fake_image_block = Block.create(
        client, file_id=file.id, content=bytes([1, 3, 5]), mime_type=MimeTypes.PNG
    )
    text_and_image_key = [Block(text="caption this", mime_type=MimeTypes.TXT), fake_image_block]
    image_action = Action(tool="image_tool", input=text_and_image_key)
    cache.update(key=text_and_image_key, value=image_action)
    action = cache.lookup(key=text_and_image_key)
    assert action
    assert action.tool == "image_tool"
    assert action.input == text_and_image_key

    cache.clear()
    assert not cache.lookup(key=text_and_image_key)


@pytest.mark.usefixtures("client")
def test_action_cache(client: Steamship):
    context_keys = {"id": "test"}
    cache = ActionCache.get_or_create(client=client, context_keys=context_keys)

    file = File.create(client=client, handle="whocares")
    fake_image_block = Block.create(
        client, file_id=file.id, content=bytes([1, 3, 5]), mime_type=MimeTypes.PNG
    )
    text_and_image = [Block(text="caption this", mime_type=MimeTypes.TXT), fake_image_block]
    key = Action(tool="fake_tool", input=text_and_image)
    assert not cache.lookup(key)

    cache.update(key=key, value=text_and_image)
    blocks = cache.lookup(key)
    assert blocks
    assert blocks == text_and_image

    cache.update(key=key, value=[Block(text="other")])
    blocks = cache.lookup(key)
    assert blocks
    assert blocks[0].text == "other"

    cache.delete(key)
    assert not cache.lookup(key)

    cache.update(key=key, value=text_and_image)
    cache.clear()
    assert not cache.lookup(key)
