from typing import List
from dataclasses import dataclass
from nludb.types.base import Request, Model
from nludb.types.search import Hit
from nludb.api.base import ApiBase 

@dataclass
class ClassifierCreateRequest(Request):
  model: str
  name: str = None
  upsert: bool = True
  save: bool = True
  labels: List[str] = None

@dataclass
class ClassifierCreateResponse(Model):
  classifierId: str = None

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "ClassifierCreateResponse":
    return ClassifierCreateResponse(
      classifierId = d.get('classifierId', None),
    )

@dataclass
class ClassifyRequest(Request):
  docs: List[str]
  classifierId: str = None
  model: str = None
  labels: List[str] = None
  k: int = None

@dataclass
class ClassifyResponse(Model):
  classifierId: str = None
  model: str = None
  hits: List[List[Hit]] = None

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "ClassifyResponse":
    hits = [[Hit.safely_from_dict(h) for h in innerList] for innerList in (d.get("hits", []) or [])]
    return ClassifyResponse(
      classifierId = d.get('classifierId', None),
      model = d.get('model', None),
      hits = hits
    )

@dataclass
class LabelInsertRequest(Request):
  value: str
  externalId: str = None
  externalType: str = None
  metadata: str = None

@dataclass
class LabelInsertResponse(Model):
  labelId: str
  value: str
  externalId: str = None
  externalType: str = None
  metadata: str = None

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "LabelInsertResponse":
    return LabelInsertResponse(
      labelId = d.get('labelId', None),
      value = d.get('value', None),
      externalId = d.get('externalId', None),
      externalType = d.get('externalType', None),
      metadata = d.get('metadata', None),
    )

@dataclass
class ClassifierDeleteResponse(Model):
  classifierId: str = None

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "ClassifierDeleteResponse":
    return ClassifierDeleteResponse(
      classifierId = d.get('classifierId', None),
    )
