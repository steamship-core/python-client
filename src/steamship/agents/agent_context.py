from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import BaseModel

from steamship import Block, PluginInstance, Steamship, Workspace


class AgentContext(BaseModel, ABC):
    # The
    client: Steamship

    @abstractmethod
    def update_blocks(self, blocks: List[Block]):
        pass

    @abstractmethod
    def append_log(self, message: str):
        pass

    @abstractmethod
    def default_text_generator(self) -> PluginInstance:
        pass

    import contextlib

    @contextlib.contextmanager
    @staticmethod
    def temporary(client: Optional[Steamship] = None) -> "AgentContext":
        client = client or Steamship()
        workspace = Workspace.create(client=client)
        context = AgentContext(client=client)
        yield context
        workspace.delete()
