import json
from dataclasses import dataclass

@dataclass
class Hit:
  index: int = None
  value: str = None
  score: float = None 
  externalId: str = None
  externalType: str = None
  metadata: any = None

  @staticmethod
  def safely_from_dict(d: any) -> "Hit":
    metadata = d.get("metadata", None)
    if metadata is not None:
      try:
        metadata = json.loads(metadata)
      except:
        pass

    return Hit(
      index=d.get("index", None),
      value=d.get("value", d.get("text", None)),
      score=d.get("score", None),
      externalId=d.get("externalId", None),
      externalType=d.get("externalType", None),
      metadata=metadata
    )