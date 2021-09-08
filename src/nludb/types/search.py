import json
from dataclasses import dataclass

@dataclass
class Hit:
  id: str = None
  index: int = None
  indexSource: str = None
  value: str = None
  score: float = None 
  externalId: str = None
  externalType: str = None
  metadata: any = None
  query: str = None

  @staticmethod
  def safely_from_dict(d: any) -> "Hit":
    metadata = d.get("metadata", None)
    if metadata is not None:
      try:
        metadata = json.loads(metadata)
      except:
        pass

    return Hit(
      id=d.get("id", None),
      index=d.get("index", None),
      indexSource=d.get("indexSource", None),
      value=d.get("value", d.get("text", None)),
      score=d.get("score", None),
      externalId=d.get("externalId", None),
      externalType=d.get("externalType", None),
      metadata=metadata,
      query=d.get("query", None)
    )