import uuid
from typing import List

from steamship import Block
from steamship.agents.agent_context import AgentContext
from steamship.agents.tools.workspace_tool import WorkspaceTool
from steamship.utils.kv_store import KeyValueStore


class ExampleCacheTool(WorkspaceTool):
    name = "CacheTool"
    human_description = "In-Memory Key-Value Store"
    ai_description = ("Used to store and lookup values by a known key.",)
    store: KeyValueStore

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.store = KeyValueStore(client=self.client, store_identifier=f"cache-{uuid.uuid4()}")

    def run(self, tool_input: List[Block], context: AgentContext) -> List[Block]:
        pass
