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


def is_assistant_function_message(block: Block) -> bool:
    is_function_selection = get_tag(block.tags, kind=TagKind.FUNCTION_SELECTION)
    return is_assistant_message(block) and is_function_selection


def is_user_history_message(block: Block) -> bool:
    return is_user_message(block) or (
        is_assistant_message(block) and not is_assistant_function_message(block)
    )


class MessageWindowMessageSelector(MessageSelector):
    k: int

    def get_messages(self, messages: List[Block]) -> List[Block]:
        msgs = messages[:]
        msgs.pop()  # don't add the current prompt to the memory
        history_msgs = [
            msg for msg in msgs if is_user_history_message(msg)
        ]  # filter to only user history messages
        if len(history_msgs) <= (self.k * 2):
            return history_msgs

        selected_msgs = []
        limit = self.k * 2
        scope = history_msgs[len(history_msgs) - limit :]
        for block in scope:
            if is_user_history_message(block):
                selected_msgs.append(block)

        return selected_msgs


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
        msgs.pop()  # don't add the current prompt to the memory
        history_msgs = [
            msg for msg in msgs if is_user_history_message(msg)
        ]  # filter to only user history messages
        for block in reversed(history_msgs):
            if block.chat_role != RoleTag.SYSTEM and current_tokens < self.max_tokens:
                block_tokens = tokens(block)
                if block_tokens + current_tokens < self.max_tokens:
                    selected_messages.append(block)
                    current_tokens += block_tokens

        return reversed(selected_messages)
