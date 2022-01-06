from dataclasses import dataclass
from nludb.types.base import Request, Response
from nludb.types.block import Block
from nludb.api.base import ApiBase

@dataclass
class ConvertRequest(Request):
  type: str
  model: str = None
  id: str = None
  handle: str = None
  name: str = None

@dataclass
class ConvertResponse(Response):
  client: ApiBase = None
  root: Block = None

  @staticmethod
  def safely_from_dict(d: any = None, client: ApiBase = None) -> "ConvertResponse":
    if d is None:
        return None
    return ConvertResponse(
      client = client,
      block = Block.safely_from_dict(d.get('block', None), client=client)
    )
