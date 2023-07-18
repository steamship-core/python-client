import uuid
from typing import List

import pytest

from steamship import Block, DocTag
from steamship.agents.schema import ChatHistory
from steamship.agents.schema.message_selectors import MessageSelector
from steamship.client import Steamship
from steamship.data import TagKind
from steamship.data.tags.tag_constants import ChatTag, RoleTag, TagValueKey


@pytest.mark.usefixtures("client")
def test_chat_create(client: Steamship):
    chat = ChatHistory.get_or_create(client, context_keys={"test_id": uuid.uuid4().hex})

    assert chat.client is not None
    assert isinstance(chat, ChatHistory)
    assert len(chat.tags) == 3
    assert chat.tags[0].kind == TagKind.DOCUMENT
    assert chat.tags[0].name == DocTag.CHAT


@pytest.mark.usefixtures("client")
def test_chat_append_system(client: Steamship):
    chat = ChatHistory.get_or_create(client, context_keys={"test_id": uuid.uuid4().hex})

    chat.append_system_message(text="some system text")
    chat.refresh()

    assert len(chat.messages) == 1
    assert chat.messages[0].text == "some system text"

    assert len(chat.messages[0].tags) == 2
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

    assert len(chat.messages[0].tags) == 2
    assert chat.messages[0].tags[0].kind == TagKind.CHAT
    assert chat.messages[0].tags[0].name == ChatTag.ROLE
    assert chat.messages[0].tags[0].value == {TagValueKey.STRING_VALUE: RoleTag.USER}


@pytest.mark.usefixtures("client")
def test_chat_history_clear(client: Steamship):
    history = ChatHistory.get_or_create(client, context_keys={"test_id": uuid.uuid4().hex})
    history.append_user_message(text="some user text")
    history.append_assistant_message(text="some ai response")
    history.refresh()

    assert len(history.messages) == 2

    history.clear()

    assert len(history.messages) == 0


@pytest.mark.usefixtures("client")
def test_chat_history_delete_some(client: Steamship):
    history = ChatHistory.get_or_create(client, context_keys={"test_id": uuid.uuid4().hex})
    history.append_user_message(text="some user text")
    history.append_assistant_message(text="some ai response")
    history.append_system_message(text="you shall not pass!")
    history.refresh()

    assert len(history.messages) == 3

    blocks = history.search("pass").wait().to_ranked_blocks()
    assert len(blocks) == 1
    assert blocks[0].text == "you shall not pass!"

    class AssistantMessageSelector(MessageSelector):
        def get_messages(self, messages: List[Block]) -> List[Block]:
            selected = []
            for message in messages:
                if message.chat_role == RoleTag.ASSISTANT:
                    selected.append(message)
            return selected

    history.delete_messages(AssistantMessageSelector())

    assert len(history.messages) == 2

    blocks = history.search("pass").wait().to_ranked_blocks()
    assert len(blocks) == 1
    assert blocks[0].text == "you shall not pass!"


@pytest.mark.usefixtures("client")
def test_chat_history_delete_no_selector(client: Steamship):
    history = ChatHistory.get_or_create(client, context_keys={"test_id": uuid.uuid4().hex})
    history.append_user_message(text="some user text")
    history.append_assistant_message(text="some ai response")
    history.append_system_message(text="you shall not pass!")
    history.refresh()

    assert len(history.messages) == 3

    history.delete_messages(None)

    assert len(history.messages) == 3
