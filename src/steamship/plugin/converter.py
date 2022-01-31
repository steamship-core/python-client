from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict

from steamship.base import Client
from steamship.data.block import Block
from steamship.plugin.service import PluginService, PluginRequest, PluginResponse


@dataclass
class ConvertRequest:
    type: str = None
    model: str = None
    id: str = None
    handle: str = None
    name: str = None

    @staticmethod
    def from_dict(d: any) -> "ConvertRequest":
        return ConvertRequest(
            type=d.get('type', None),
            model=d.get('model', None),
            id=d.get('id', None),
            handle=d.get('handle', None),
            name=d.get('name', None)
        )


@dataclass
class ConvertResponse():
    root: Block = None

    @staticmethod
    def from_dict(d: any = None, client: Client = None) -> "ConvertResponse":
        if d is None:
            return None

        return ConvertResponse(
            root=Block.from_dict(d.get('root', None), client=client)
        )

    def to_dict(self) -> Dict:
        if self.root is None:
            return dict()
        return dict(root=self.root.to_dict())


class Converter(PluginService):
    @abstractmethod
    def _run(self, request: PluginRequest[ConvertRequest]) -> PluginResponse[ConvertResponse]:
        pass
