from dataclasses import dataclass
from typing import Dict

from steamship.base import Client
from steamship.data.file import File

@dataclass
class BlockAndTagPluginOutput():
    file: File.CreateRequest = None

    @staticmethod
    def from_dict(d: any = None, client: Client = None) -> "BlockAndTagPluginOutput":
        if d is None:
            return None

        return BlockAndTagPluginOutput(
            file=File.CreateRequest.from_dict(d.get('file', None), client=client)
        )

    def to_dict(self) -> Dict:
        if self.file is None:
            return dict()
        return dict(file=self.file.to_dict())
