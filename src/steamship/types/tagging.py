import json
from dataclasses import dataclass
from typing import List, Dict, Callable
from steamship.types.base import Request, Model
from steamship.types.block import Block
from steamship.client.base import ApiBase

@dataclass
class TagResponse(Model):
  blocks: List[Block] = None

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "TagResponse":
    blocks = [Block.safely_from_dict(h) for h in (d.get("blocks", []) or [])]
    return TagResponse(
      blocks=blocks
    )

@dataclass
class TagRequest(Request):
  blocks: List[str] = None
  fileId: str = None
  parsedBlocks: List[Block] = None
  model: str = None
  metadata: any = None

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "TagRequest":
    metadata = d.get("metadata", None)
    if metadata is not None:
      try:
        metadata = json.loads(metadata)
      except:
        pass

    parsedBlocks = [Block.safely_from_dict(dd) for dd in (d.get("parsedBlocks", []) or [])]
      
    return TagRequest(
      blocks=(d.get("blocks", []) or []),
      fileId=d.get('fileId', None),
      parsedBlocks=parsedBlocks,
      model=d.get("model", None),
      metadata=metadata
    )

