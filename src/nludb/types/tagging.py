import json
from dataclasses import dataclass
from typing import List, Dict, Callable
from nludb.types.base import NludbRequest, NludbResponseData
from nludb.types.parsing import Doc

@dataclass
class TagResponse(NludbResponseData):
  docs: List[Doc] = None

  @staticmethod
  def safely_from_dict(d: any) -> "TagResponse":
    docs = [Doc.safely_from_dict(h) for h in (d.get("docs", []) or [])]
    return TagResponse(
      docs=docs
    )

@dataclass
class TagRequest(NludbRequest):
  docs: List[Doc] = None
  model: str = None
  metadata: any = None

  @staticmethod
  def safely_from_dict(d: any) -> "TagRequest":
    metadata = d.get("metadata", None)
    if metadata is not None:
      try:
        metadata = json.loads(metadata)
      except:
        pass

    return TagRequest(
      docs=(d.get("docs", []) or []),
      model=d.get("model", None),
      metadata=metadata
    )

