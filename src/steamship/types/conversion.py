from dataclasses import dataclass

from steamship.client.base import ApiBase
from steamship.types.base import Model
from steamship.types.block import Block


@dataclass
class ConvertResponse(Model):
    client: ApiBase = None
    root: Block = None

    @staticmethod
    def from_dict(d: any = None, client: ApiBase = None) -> "ConvertResponse":
        if d is None:
            return None
        return ConvertResponse(
            client=client,
            root=Block.from_dict(d.get('root', None), client=client)
        )
