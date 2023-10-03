from abc import ABC, abstractmethod
from typing import List

import tiktoken
from pydantic.main import BaseModel

from steamship import Block
from steamship.data.tags.tag_constants import RoleTag, TagKind
from steamship.data.tags.tag_utils import get_tag


class MessageSelector(BaseModel, ABC):
    @abstractmethod
    def get_messages(self, messages: List[Block]) -> List[Block]:
        pass


class NoMessages(MessageSelector):
    def get_messages(self, messages: List[Block]) -> List[Block]:
        return []


def is_user_message(block: Block) -> bool:
    role = block.chat_role
    return role == RoleTag.USER


def is_assistant_message(block: Block) -> bool:
    role = block.chat_role
    return role == RoleTag.ASSISTANT


def is_function_message(block: Block) -> bool:
    is_function_selection = get_tag(block.tags, kind=TagKind.FUNCTION_SELECTION)
    return is_function_selection


def is_tool_function_message(block: Block) -> bool:
    is_function_call = get_tag(block.tags, kind=TagKind.ROLE, name=RoleTag.FUNCTION)
    return is_function_call


def is_user_history_message(block: Block) -> bool:
    return is_user_message(block) or (
        is_assistant_message(block) and not is_function_message(block)
    )


class MessageWindowMessageSelector(MessageSelector):
    k: int

    def get_messages(self, messages: List[Block]) -> List[Block]:
        msgs = messages[:]
        # msgs.pop()
        have_seen_user_message = False
        if is_user_message(msgs[-1]):
            have_seen_user_message = True
            msgs.pop()  # don't add the current prompt to the memory
        selected_msgs = []
        conversation_messages = 0
        limit = self.k * 2
        message_index = len(msgs) - 1
        while (conversation_messages < limit) and (message_index > 0):
            # TODO(dougreid): i _think_ we don't need the function return if we have a user-assistant pair
            # but, for safety here, we try to add non-current function blocks from past iterations.
            block = msgs[message_index]
            if is_user_message(block):
                have_seen_user_message = True
            if is_user_history_message(block):
                selected_msgs.append(block)
                conversation_messages += 1
            elif have_seen_user_message and (
                is_function_message(block) or is_tool_function_message(block)
            ):
                # conditionally append working function call messages
                selected_msgs.append(block)
            message_index -= 1

        return reversed(selected_msgs)


def tokens(block: Block) -> int:
    enc = tiktoken.get_encoding("p50k_base")
    tokenized_text = enc.encode(block.text)
    return len(tokenized_text)


class TokenWindowMessageSelector(MessageSelector):
    max_tokens: int

    def get_messages(self, messages: List[Block]) -> List[Block]:
        selected_messages = []
        current_tokens = 0

        msgs = messages[:]
        if is_user_message(msgs[-1]):
            msgs.pop()  # don't add the current prompt to the memory

        for block in reversed(msgs):
            if is_user_history_message(block) and current_tokens < self.max_tokens:
                block_tokens = tokens(block)
                if block_tokens + current_tokens < self.max_tokens:
                    selected_messages.append(block)
                    current_tokens += block_tokens

        return reversed(selected_messages)
