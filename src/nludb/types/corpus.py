from typing import List
from dataclasses import dataclass
from nludb.types.base import NludbRequest, NludbResponseData, str_to_metadata

@dataclass
class CreateCorpusResponse(NludbResponseData):
  id: str = None
  name: str = None
  description: str = None
  externalId: str = None
  externalType: str = None
  isPublic: bool = None
  metadata: str = None

  @staticmethod
  def safely_from_dict(d: any) -> "Corpus":
    return Corpus(
      corpusId = d.get('id', None),
      name = d.get('name', None),
      description = d.get('description', None),
      externalId = d.get('externalId', None),
      externalType = d.get('externalType', None),
      metadata = str_to_metadata(d.get("metadata", None)),
    )

@dataclass
class CreateCorpusRequest(NludbRequest):
  corpusId: str = None
  name: str = None
  description: str = None
  externalId: str = None
  externalType: str = None
  isPublic: bool = None
  metadata: str = None
  upsert: bool = None

@dataclass
class DeleteCorpusRequest(NludbRequest):
  corpusId: str

@dataclass
class ListPublicCorporaRequest(NludbRequest):
  pass

@dataclass
class ListPrivateCorporaRequest(NludbRequest):
  pass

@dataclass
class ListCorporaResponse(NludbRequest):
  corpora: List[Corpus]

  @staticmethod
  def safely_from_dict(d: any) -> "ListCorporaResponse":
    return ListCorporaResponse(
      models = [Corpus.safely_from_dict(x) for x in (d.get("corpus", []) or [])]
    )
