import json
from dataclasses import dataclass
from typing import List, Dict, Callable
from steamship.types.base import Request, Model
from steamship.types.parsing import Doc
from steamship.client.base import ApiBase

@dataclass
class TagResponse(Model):
  docs: List[Doc] = None

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "TagResponse":
    docs = [Doc.safely_from_dict(h) for h in (d.get("docs", []) or [])]
    return TagResponse(
      docs=docs
    )

@dataclass
class TagRequest(Request):
  docs: List[str] = None
  fileId: str = None
  parsedDocs: List[Doc] = None
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

    parsedDocs = [Doc.safely_from_dict(dd) for dd in (d.get("parsedDocs", []) or [])]
      
    return TagRequest(
      docs=(d.get("docs", []) or []),
      fileId=d.get('fileId', None),
      parsedDocs=parsedDocs,
      model=d.get("model", None),
      metadata=metadata
    )

