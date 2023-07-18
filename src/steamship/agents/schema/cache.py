import hashlib
import json
import logging
from typing import Dict, List, Optional

from steamship import Block, MimeTypes, Steamship
from steamship.agents.schema.action import Action, FinishAction
from steamship.utils.kv_store import KeyValueStore


def _blocks_to_cache_dict(value: List[Block]) -> Dict[str, any]:
    """Attempts to convert a list of blocks to key-store-safe dictionary.

    Convention: {'blocks':[{'id': <block_id>}, {'text': <some_text>}]}
    """

    if not value:
        return {}
    if not isinstance(value, list):
        return {}
    blocks = []
    for block in value:
        if block.id:
            blocks.append({"id": block.id})
        else:
            # TODO(dougreid): safe assumption about temporary blocks?
            blocks.append({"text": block.text})
    return {"blocks": blocks}


def _blocks_from_cache_dict(client: Steamship, value: Dict[str, any]) -> List[Block]:
    """Attempts to convert a key-store-safe dictionary to a list of blocks.

    Convention: {'blocks':[{'id': <block_id>}, {'text': <some_text>}]}
    """
    if block_list := value.get("blocks"):
        return_blocks = []
        for b in block_list:
            if block_id := b.get("id"):
                return_blocks.append(Block.get(client, _id=block_id))
            else:
                return_blocks.append(Block(text=b.get("text"), mime_type=MimeTypes.TXT))
        return return_blocks

    return []


class ActionCache:
    """Provide persistent cache layer for AgentContext that allows lookups of output blocks from Actions.

    Use this cache to eliminate calls to Tools.

    NOTE: EXPERIMENTAL.
    """

    client: Steamship
    key_value_store: KeyValueStore

    def __init__(self, client: Steamship, key_value_store: KeyValueStore):
        self.client = client
        self.key_value_store = key_value_store

    @staticmethod
    def get_or_create(client: Steamship, context_keys: Dict[str, str]):
        cache_handle = (
            f"actioncache-{hashlib.sha256(json.dumps(context_keys).encode('utf-8')).hexdigest()}"
        )
        return ActionCache(
            client=client,
            key_value_store=KeyValueStore(client=client, store_identifier=cache_handle),
        )

    @staticmethod
    def _cache_key_for(action: Action) -> str:
        if isinstance(action, Action):
            key = f"{action.tool}"
            for block in action.input:
                if block.is_text():
                    key = f"{key}-{block.text}"
                else:
                    key = f"{key}-{block.id}"
        else:
            key = f"unknown-{json.dumps(action)}"

        return f"sk-{hashlib.sha256(key.encode('utf-8')).hexdigest()}"

    def lookup(self, key: Action) -> Optional[List[Block]]:
        cache_key = ActionCache._cache_key_for(key)
        value = self.key_value_store.get(key=cache_key) or None
        if value:
            logging.debug(f"cache hit for {cache_key}")
            return _blocks_from_cache_dict(self.client, value)

        logging.debug(f"cache miss for {cache_key}")
        return None

    def clear(self) -> None:
        self.key_value_store.reset()

    def update(self, key: Action, value: List[Block]):
        # TODO: should this be synchronous and wait?
        self.key_value_store.set(
            key=ActionCache._cache_key_for(key), value=_blocks_to_cache_dict(value)
        )
        return

    def delete(self, key: Action) -> bool:
        return self.key_value_store.delete(key=ActionCache._cache_key_for(key))


class LLMCache:
    """Provide persistent cache layer for AgentContext that allows lookups of Actions from LLM prompts.

    Use this cache to eliminate calls to LLMs for Tool selection and direct responses.

    NOTE: EXPERIMENTAL.
    """

    client: Steamship
    key_value_store: KeyValueStore

    def __init__(self, client: Steamship, key_value_store: KeyValueStore):
        self.client = client
        self.key_value_store = key_value_store

    @staticmethod
    def get_or_create(client: Steamship, context_keys: Dict[str, str]):
        cache_handle = (
            f"llmcache-{hashlib.sha256(json.dumps(context_keys).encode('utf-8')).hexdigest()}"
        )
        return LLMCache(
            client=client,
            key_value_store=KeyValueStore(client=client, store_identifier=cache_handle),
        )

    @staticmethod
    def _cache_key_for(inputs: List[Block]) -> str:
        if isinstance(inputs, list):
            key = "llm"
            for block in inputs:
                if block.is_text():
                    key = f"{key}-{block.text}"
                else:
                    key = f"{key}-{block.id}"
        else:
            key = f"unknown-{json.dumps(inputs)}"
        return f"sk-{hashlib.sha256(key.encode('utf-8')).hexdigest()}"

    def _action_from_value(self, value: dict) -> Action:
        input_blocks = []
        if in_blocks := value.get("input"):
            input_blocks = _blocks_from_cache_dict(self.client, in_blocks)

        output_blocks = []
        if out_blocks := value.get("output"):
            output_blocks = _blocks_from_cache_dict(self.client, out_blocks)

        if value.get("tool") == "Agent-FinishAction":
            return FinishAction(input=input_blocks, output=output_blocks)

        return Action(tool=value.get("tool"), input=input_blocks, output=output_blocks)

    def lookup(self, key: List[Block]) -> Optional[Action]:
        cache_key = LLMCache._cache_key_for(key)
        value = self.key_value_store.get(key=cache_key) or None
        if value:
            logging.debug(f"cache hit for {cache_key}")
            return self._action_from_value(value)

        logging.debug(f"cache miss for {cache_key}")
        return None

    def clear(self) -> None:
        self.key_value_store.reset()

    def update(self, key: List[Block], value: Action):
        # TODO: should this be synchronous and wait?
        action_dict = {
            "tool": value.tool,
            "input": _blocks_to_cache_dict(value.input),
            "output": _blocks_to_cache_dict(value.output),
        }
        self.key_value_store.set(key=LLMCache._cache_key_for(key), value=action_dict)
        return

    def delete(self, key: List[Block]) -> bool:
        return self.key_value_store.delete(key=LLMCache._cache_key_for(key))
