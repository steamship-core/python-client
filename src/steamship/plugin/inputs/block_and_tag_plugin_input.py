from typing import Dict

from steamship import File
from steamship.base import Client

from dataclasses import dataclass

@dataclass
class BlockAndTagPluginInput:
    file: File = None

    @staticmethod
    def from_dict(d: any = None, client: Client = None) -> "BlockAndTagPluginInput":
        if d is None:
            return None

        return BlockAndTagPluginInput(
            file=File.from_dict(d.get('file', None), client=client)
        )

    def to_dict(self) -> Dict:
        if self.file is None:
            return dict()
        return dict(file=self.file.to_dict())

