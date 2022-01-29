from typing import Dict
from dataclasses import dataclass

@dataclass
class ImporterRequest:
  metadata: Dict = None

  @staticmethod
  def from_dict(d: any) -> "ImporterRequest":
    return ImporterRequest(
      metadata = d.get('metadata', {})
    )


