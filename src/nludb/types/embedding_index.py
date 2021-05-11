from dataclasses import dataclass
from nludb.types.base import NludbRequest, NludbResponse

class EmbeddingIndexModels:
  QA = "st_msmarco_distilbert_base_v3"
  SIMILARITY = "st_paraphrase_distilroberta_base_v1"

  DEFAULT_QA = "st_msmarco_distilbert_base_v3"
  DEFAULT_SIMILARITY = "st_paraphrase_distilroberta_base_v1"

@dataclass
class IndexCreateRequest(NludbRequest):
  name: str
  model: str
  upsert: bool = True
  externalId: str = None
  externalType: str = None
  metadata: any = None

@dataclass
class IndexCreateResponse(NludbResponse):
  id: str

@dataclass
class IndexInsertRequest(NludbRequest):
  indexId: str
  value: str
  externalId: str = None
  externalType: str = None
  metadata: any = None
  reindex: bool = True

@dataclass
class IndexInsertResponse(NludbResponse):
  id: str

@dataclass
class IndexEmbedRequest(NludbRequest):
  indexId: str

@dataclass
class IndexEmbedResponse(NludbResponse):
  id: str

@dataclass
class IndexSearchRequest(NludbRequest):
  indexId: str
  query: str
  k: int = 1
  includeMetadata: bool = False

@dataclass
class IndexSearchResponse(NludbResponse):
  hits: str
