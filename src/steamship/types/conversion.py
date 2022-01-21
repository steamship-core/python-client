from dataclasses import dataclass
from steamship.types.base import Request, Model
from steamship.types.block import Block
from steamship.client.base import ApiBase

@dataclass
class ConvertRequest(Request):
  type: str
  model: str = None
  id: str = None
  handle: str = None
  name: str = None

@dataclass
class ConvertResponse(Model):
  client: ApiBase = None
  root: Block = None

  @staticmethod
  def safely_from_dict(d: any = None, client: ApiBase = None) -> "ConvertResponse":
    if d is None:
        return None
    return ConvertResponse(
      client = client,
      root = Block.safely_from_dict(d.get('root', None), client=client)
    )
