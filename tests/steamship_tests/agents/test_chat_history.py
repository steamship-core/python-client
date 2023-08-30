import pytest

from steamship import Steamship
from steamship.agents.schema.chathistory import ChatHistory
from steamship.data.tags.tag_constants import ChatTag, TagKind
from steamship.data.tags.tag_utils import get_tag


@pytest.mark.usefixtures("client")
def test_chat_history_index_init(client: Steamship):

    context_keys = {}

    chat_history = ChatHistory.get_or_create(client, context_keys)
    assert chat_history.embedding_index is not None
    assert chat_history.embedding_index.handle is not None
    assert chat_history.embedding_index.embedder.id is not None

    # It should be marked as a Chat History
    assert get_tag(chat_history.tags, kind=TagKind.CHAT, name=ChatTag.HISTORY)

    chat_history_fetched = ChatHistory.get_or_create(client, context_keys)
    assert chat_history_fetched.embedding_index is not None
    assert chat_history.embedding_index.handle == chat_history_fetched.embedding_index.handle
    assert (
        chat_history.embedding_index.embedder.id == chat_history_fetched.embedding_index.embedder.id
    )

    # It should be marked as a Chat History
    assert get_tag(chat_history_fetched.tags, kind=TagKind.CHAT, name=ChatTag.HISTORY)

    block = chat_history.append_user_message(text="Hi. My birthday is today")
    chunk_tag = [tag for tag in block.tags if tag.name == ChatTag.CHUNK][0]
    assert chunk_tag.start_idx == 0
    assert chunk_tag.end_idx == 24

    # It should be marked as a Chat Message
    assert get_tag(block.tags, kind=TagKind.CHAT, name=ChatTag.MESSAGE)

    chat_history.append_user_message("I like bananas")
    chat_history.append_user_message("I also like shiny cars")
    chat_history.append_user_message("And I like programming agents")

    vehicle_search = chat_history.search("vehicle").wait()
    assert vehicle_search.items[0].tag.text == "I also like shiny cars"

    coding_search = chat_history.search("coding").wait()
    assert coding_search.items[0].tag.text == "And I like programming agents"
