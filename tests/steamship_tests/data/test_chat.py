import uuid

import pytest

from steamship import DocTag
from steamship.agents.context.chathistory import ChatHistory
from steamship.client import Steamship
from steamship.data import TagKind
from steamship.data.tags.tag_constants import ChatTag, RoleTag, TagValueKey


@pytest.mark.usefixtures("client")
def test_chat_create(client: Steamship):
    chat = ChatHistory.get_or_create(client, context_keys={"test_id": uuid.uuid4().hex})

    assert chat.client is not None
    assert isinstance(chat, ChatHistory)
    assert len(chat.tags) == 1
    assert chat.tags[0].kind == TagKind.DOCUMENT
    assert chat.tags[0].name == DocTag.CHAT


@pytest.mark.usefixtures("client")
def test_chat_append_system(client: Steamship):
    chat = ChatHistory.get_or_create(client, context_keys={"test_id": uuid.uuid4().hex})

    chat.append_system_message(text="some system text")
    chat.refresh()

    assert len(chat.messages) == 1
    assert chat.messages[0].text == "some system text"

    assert len(chat.messages[0].tags) == 1
    assert chat.messages[0].tags[0].kind == TagKind.CHAT
    assert chat.messages[0].tags[0].name == ChatTag.ROLE
    assert chat.messages[0].tags[0].value == {TagValueKey.STRING_VALUE: RoleTag.SYSTEM}


@pytest.mark.usefixtures("client")
def test_chat_append_user(client: Steamship):
    chat = ChatHistory.get_or_create(client, context_keys={"test_id": uuid.uuid4().hex})

    chat.append_user_message(text="some user text")
    chat.refresh()

    assert len(chat.messages) == 1
    assert chat.messages[0].text == "some user text"

    assert len(chat.messages[0].tags) == 1
    assert chat.messages[0].tags[0].kind == TagKind.CHAT
    assert chat.messages[0].tags[0].name == ChatTag.ROLE
    assert chat.messages[0].tags[0].value == {TagValueKey.STRING_VALUE: RoleTag.USER}
