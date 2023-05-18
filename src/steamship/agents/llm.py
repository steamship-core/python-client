from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel

from steamship import Block, MimeTypes, Tag, File, PluginInstance, Steamship
from steamship.data import TagKind
from steamship.data.tags.tag_constants import RoleTag


class LLM(BaseModel, ABC):

    @abstractmethod
    def complete(self, prompt: str) -> List[Block]:
        pass


class OpenAI(LLM):
    generator: PluginInstance
    client: Steamship

    def __init__(self, client, *args, **kwargs):
        client = client
        generator = client.use_plugin("gpt-4")
        super().__init__(client=client, generator=generator, *args, **kwargs)

    def complete(self, prompt: str) -> List[Block]:
        file = File.create(self.client, blocks=[Block(
            text=prompt,
            tags=[Tag(kind=TagKind.ROLE, name=RoleTag.SYSTEM)],
            mime_type=MimeTypes.TXT,
        )])

        action_task = self.generator.generate(input_file_id=file.id)  # This needs a helper class
        action_task.wait()
        return action_task.output.blocks
