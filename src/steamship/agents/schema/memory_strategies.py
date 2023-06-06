from typing import List

import tiktoken

from steamship import Block
from steamship.agents.memory.chathistory import ChatHistory, MemoryStrategy
from steamship.data.tags.tag_constants import RoleTag


class NoMemory(MemoryStrategy):
    def messages(self, chat_history: ChatHistory) -> List[Block]:
        return []


def is_user_message(block: Block) -> bool:
    role = block.chat_role
    return role == RoleTag.USER


def is_assistant_message(block: Block) -> bool:
    role = block.chat_role
    return role == RoleTag.ASSISTANT


class MessageWindowMemoryStrategy(MemoryStrategy):
    k: int
    # k: Field(default=4, ge=1, description="Number of message pairs to return from history. A message pair is a
    # single set of messages exchanged between a user and an assistant."

    def messages(self, chat_history: ChatHistory) -> List[Block]:
        all_messages = chat_history.messages
        all_messages.pop()  # don't add the current prompt to the memory
        print(f"message len: {len(all_messages)}")
        if len(all_messages) <= (self.k * 2):
            return all_messages

        msgs = []
        limit = self.k * 2
        scope = all_messages[len(all_messages) - limit :]
        print(f"scope: {scope}")
        for block in scope:
            if is_user_message(block) or is_assistant_message(block):
                print("appending message")
                msgs.append(block)

        return msgs


def tokens(block: Block) -> int:
    enc = tiktoken.get_encoding("p50k_base")
    tokenized_text = enc.encode(block.text)
    return len(tokenized_text)


class TokenWindowMemoryStrategy(MemoryStrategy):
    max_tokens: int
    # Field(default=2000, ge=1, description="Number of tokens to return from history.")

    def messages(self, chat_history: ChatHistory) -> List[Block]:
        messages = []
        current_tokens = 0

        # TODO: this seems like a flaw in the way we use ChatHistory
        all_messages = chat_history.messages
        all_messages.pop()  # don't add the current prompt to the memory
        for block in reversed(all_messages):
            if block.chat_role != RoleTag.SYSTEM and current_tokens < self.max_tokens:
                block_tokens = tokens(block)
                if block_tokens + current_tokens < self.max_tokens:
                    messages.append(block)
                    current_tokens += block_tokens

        return reversed(messages)
