from dataclasses import dataclass
from steamship.types.base import Request, Model
from steamship.types.block import Block
from steamship.client.base import ApiBase


@dataclass
class ConvertResponse(Model):
  client: ApiBase = None
  root: Block = None

  @staticmethod
  def from_dict(d: any = None, client: ApiBase = None) -> "ConvertResponse":
    if d is None:
        return None
    return ConvertResponse(
      client = client,
      root = Block.from_dict(d.get('root', None), client=client)
    )
