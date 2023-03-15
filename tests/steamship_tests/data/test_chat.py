import pytest

from steamship import DocTag
from steamship.client import Steamship
from steamship.data import TagKind
from steamship.data.chat import Chat
from steamship.data.tags.tag_constants import RoleTag


@pytest.mark.usefixtures("client")
def test_chat_create(client: Steamship):
    chat = Chat.create(client)

    assert chat.client is not None
    assert isinstance(chat, Chat)
    assert len(chat.tags) == 1
    assert chat.tags[0].kind == TagKind.DOCUMENT
    assert chat.tags[0].name == DocTag.CHAT


@pytest.mark.usefixtures("client")
def test_chat_append_system(client: Steamship):
    chat = Chat.create(client)

    chat.append_system_block(text="some system text")
    chat.refresh()

    assert len(chat.blocks) == 1
    assert chat.blocks[0].text == "some system text"

    assert len(chat.blocks[0].tags) == 1
    assert chat.blocks[0].tags[0].kind == TagKind.ROLE
    assert chat.blocks[0].tags[0].name == RoleTag.SYSTEM
