from dataclasses import dataclass
from steamship.client.base import ApiBase
from steamship.types.base import Model
from steamship.types.token import Token
from typing import List


@dataclass
class Span(Model):
  client: ApiBase = None
  id: str = None
  blockId: str = None
  type: str = None
  label: str = None
  text: str = None
  startCharIdx: int = None
  endCharIdx: int = None
  startTokenIdx: int = None
  endTokenIdx: int = None

  @staticmethod
  def from_dict(d: any, client: ApiBase) -> "Span":
    if d is None:
      return None
    if 'span' in d:
      d = d['span']
    return Span(
      client = client,
      id = d.get('id', None),
      blockId = d.get('blockId', None),
      type = d.get('type', None),
      label = d.get('label', None),
      text = d.get('text', None),
      startCharIdx = d.get('startCharIdx', None),
      endCharIdx = d.get('endCharIdx', None),
      startTokenIdx = d.get('startTokenIdx', None),
      endTokenIdx = d.get('endTokenIdx', None)
    )
  
  def to_dict(self) -> dict:
    return dict(
      id=self.id,
      blockId=self.blockId,
      type=self.type,
      label=self.label,
      text=self.text,
      startCharIdx=self.startCharIdx,
      endCharIdx=self.endCharIdx,
      startTokenIdx=self.startTokenIdx,
      endTokenIdx=self.endTokenIdx,
    )