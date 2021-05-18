from dataclasses import dataclass
from typing import Type, Dict

@dataclass
class NludbRequest():
  pass

@dataclass
class NludbResponse():
  pass

  @staticmethod
  def safely_from_dict(d: any) -> Dict:
    """Last resort if subclass doesn't override: pass through."""
    return d

