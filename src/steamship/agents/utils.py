from operator import attrgetter
from typing import List, Optional

from steamship import Block, MimeTypes
from steamship.agents.schema import AgentContext
from steamship.agents.schema.llm import LLM
from steamship.agents.schema.message_selectors import MessageSelector

_LLM_KEY = "llm"


def with_llm(llm: LLM, context: Optional[AgentContext] = None) -> AgentContext:
    """Sets an LLM for general purpose lookup and usage on an AgentContext."""
    if context is None:
        # TODO: should we have a default context somehow?
        context = AgentContext()
    context.metadata[_LLM_KEY] = llm
    return context


def get_llm(context: AgentContext, default: Optional[LLM] = None) -> Optional[LLM]:
    """Retrieves the LLM from the provided AgentContext (if it exists)."""
    return context.metadata.get(_LLM_KEY, default)


def build_chat_history(
    default_system_message: str, message_selector: MessageSelector, context: AgentContext
) -> List[Block]:
    # system message should have already been created in context, but we double-check for safety
    if context.chat_history.last_system_message:
        sys_msg = context.chat_history.last_system_message
    else:
        sys_msg = context.chat_history.append_system_message(
            text=default_system_message, mime_type=MimeTypes.TXT
        )
    messages: List[Block] = [sys_msg]

    messages_from_memory = []
    # get prior conversations
    if context.chat_history.is_searchable():
        messages_from_memory.extend(
            context.chat_history.search(context.chat_history.last_user_message.text, k=3)
            .wait()
            .to_ranked_blocks()
        )
        # TODO(dougreid): we need a way to threshold message inclusion, especially for small contexts

    # get most recent context
    messages_from_memory.extend(context.chat_history.select_messages(message_selector))

    messages_from_memory.sort(key=attrgetter("index_in_file"))

    # de-dupe the messages from memory
    ids = [
        sys_msg.id,
        context.chat_history.last_user_message.id,
    ]  # filter out last user message, it is appended afterwards
    for msg in messages_from_memory:
        if msg.id not in ids:
            messages.append(msg)
            ids.append(msg.id)

    # TODO(dougreid): sort by dates? we SHOULD ensure ordering, given semantic search

    # put the user prompt in the appropriate message location
    # this should happen BEFORE any agent/assistant messages related to tool selection
    messages.append(context.chat_history.last_user_message)

    return messages
