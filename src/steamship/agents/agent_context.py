import contextlib
from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import Field

from steamship import Block, PluginInstance, Steamship, Workspace
from steamship.base.model import CamelModel


class AgentContext(CamelModel, ABC):
    client: Steamship = Field(None, exclude=True)

    @abstractmethod
    def update_blocks(self, blocks: List[Block]):
        pass

    @abstractmethod
    def append_log(self, message: str):
        pass

    @abstractmethod
    def default_text_generator(self) -> PluginInstance:
        pass

    @classmethod
    @contextlib.contextmanager
    def temporary(cls, client: Optional[Steamship] = None) -> "AgentContext":
        client = client or Steamship()
        workspace = Workspace.create(client=client)
        context = cls(client=client)
        yield context
        workspace.delete()


class DebugAgentContext(AgentContext):
    client: Steamship = Field(None, exclude=True)

    def update_blocks(self, blocks: List[Block]):
        pass

    def append_log(self, message: str):
        print(f"[LOG] {message}")

    def default_text_generator(self) -> PluginInstance:
        return self.client.use_plugin("gpt-4")
