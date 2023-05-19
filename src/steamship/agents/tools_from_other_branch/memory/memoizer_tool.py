# TODO:
#
# Test writing a Memoizer;
# Memoizer(DalleTool)
#
# import uuid
# from typing import List
#
# from steamship import Block
# from steamship.agents.agent_context import AgentContext
# from steamship.agents.agents import Tool
# from steamship.utils.kv_store import KeyValueStore
#
#
# class CacheTool(Tool):
#     name = "CacheTool"
#     human_description = "In-Memory Key-Value Store"
#     ai_description = ("Used to store and lookup values by a known key.",)
#     store: KeyValueStore
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.store = KeyValueStore(client=self.client, store_identifier=f"cache-{uuid.uuid4()}")
#
#     def run(self, tool_input: List[Block], context: AgentContext) -> List[Block]:
#         pass
