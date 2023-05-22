import logging
from typing import List

import tiktoken

from steamship import Block, SteamshipError
from steamship.data.tags.tag_constants import RoleTag


def token_length(block: Block, tiktoken_encoder: str = "p50k_base") -> int:
    """Calculate num tokens with tiktoken package."""
    # create a GPT-3 encoder instance
    enc = tiktoken.get_encoding(tiktoken_encoder)
    # encode the text using the GPT-3 encoder
    tokenized_text = enc.encode(block.text)
    # calculate the number of tokens in the encoded text
    return len(tokenized_text)


# TODO: abstract this into one of N possible strategies
def filter_blocks_for_prompt_length(max_tokens: int, blocks: List[Block]) -> List[int]:

    retained_blocks = []
    total_length = 0

    # Keep all system blocks
    for block in blocks:
        if block.chat_role == RoleTag.SYSTEM:
            retained_blocks.append(block)
            total_length += token_length(block)

    # If system blocks are too long, throw error
    if total_length > max_tokens:
        raise SteamshipError(
            f"Plugin attempted to filter input to fit into {max_tokens} tokens, but the total size of system blocks was {total_length}"
        )

    # Now work backwards and keep as many blocks as we can
    num_system_blocks = len(retained_blocks)
    for block in reversed(blocks):
        if block.chat_role != RoleTag.SYSTEM and total_length < max_tokens:
            block_length = token_length(block)
            if block_length + total_length < max_tokens:
                retained_blocks.append(block)
                total_length += block_length
                logging.info(f"Adding block {block.index_in_file} of token length {block_length}")

    # If we didn't add any non-system blocks, throw error
    if len(retained_blocks) == num_system_blocks:
        raise SteamshipError(
            f"Plugin attempted to filter input to fit into {max_tokens} tokens, but no non-System blocks remained."
        )

    block_indices = [block.index_in_file for block in blocks if block in retained_blocks]
    logging.info(f"Filtered input.  Total tokens {total_length} Block indices: {block_indices}")
    return block_indices
