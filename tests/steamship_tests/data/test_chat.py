import pytest

from steamship import DocTag
from steamship.client import Steamship
from steamship.data import TagKind
from steamship.data.tags.tag_constants import RoleTag
from steamship.experimental.chatfile import ChatFile


@pytest.mark.usefixtures("client")
def test_chat_create(client: Steamship):
    chat = ChatFile.create(client, generator_instance_handle="")

    assert chat.client is not None
    assert isinstance(chat, ChatFile)
    assert len(chat.tags) == 2
    assert chat.tags[0].kind == TagKind.DOCUMENT
    assert chat.tags[0].name == DocTag.CHAT


@pytest.mark.usefixtures("client")
def test_chat_append_system(client: Steamship):
    chat = ChatFile.create(client, generator_instance_handle="")

    chat.append_system_block(text="some system text")
    chat.refresh()

    assert len(chat.blocks) == 1
    assert chat.blocks[0].text == "some system text"

    assert len(chat.blocks[0].tags) == 1
    assert chat.blocks[0].tags[0].kind == TagKind.ROLE
    assert chat.blocks[0].tags[0].name == RoleTag.SYSTEM


@pytest.mark.usefixtures("client")
def test_chat_append_user(client: Steamship):
    chat = ChatFile.create(client, generator_instance_handle="")

    chat.append_user_block(text="some user text")
    chat.refresh()

    assert len(chat.blocks) == 1
    assert chat.blocks[0].text == "some user text"

    assert len(chat.blocks[0].tags) == 1
    assert chat.blocks[0].tags[0].kind == TagKind.ROLE
    assert chat.blocks[0].tags[0].name == RoleTag.USER


@pytest.mark.usefixtures("client")
def test_chat_generate_response(client: Steamship):
    generator = client.use_plugin("test-generator")
    chat = ChatFile.create(
        client,
        generator_instance_handle=generator.handle,
        initial_system_prompt="This is my hand-crafted special instructional prompt",
    )

    chat.append_user_block(text="some user text")
    chat.append_system_block(text="This is more instructional prompt")
    output = chat.generate_next_response().wait()

    # Should GenerateOutput be able to aggregate text across blocks?
    # Should this remove need to cut .blocks?
    # Should this automatically refresh the Chat? Not sure how to do this without hijacking wait(); also would be different than File behavior
    print(output.blocks[0].text)

    chat.refresh()
    assert len(chat.blocks) == 6
    assert chat.blocks[3].text == "tpmorp lanoitcurtsni laiceps detfarc-dnah ym si sihT"
    assert chat.blocks[4].text == "txet resu emos"
    assert chat.blocks[5].text == "tpmorp lanoitcurtsni erom si sihT"
