from typing import List
from dataclasses import dataclass
from nludb.types.base import NludbRequest, NludbResponseData

class ModelType:
  embedder = "embedder"
  parser = "parser"
  classifier = "classifier"

class ModelAdapterType:
  nludbDocker = "nludbDocker"
  nludbSagemaker = "nludbSagemaker"
  huggingface = "huggingface"
  openai = "openai"

class LimitUnit:
  words = "words"
  characters = "characters"
  bytes = "bytes"

@dataclass
class Model(NludbResponseData):
  id: str = None
  name: str = None
  modelType: str = None
  url: str = None
  adapterType: str = None
  isPublic: bool = None
  handle: str = None
  description: str = None
  dimensionality: int = None
  limitAmount: int = None
  limitUnit: str = None
  apiKey: str = None
  metadata: str = None

  @staticmethod
  def safely_from_dict(d: any) -> "Model":
    return Model(
      id = d.get('id', None),
      name = d.get('name', None),
      modelType = d.get('modelType', None),
      url = d.get('url', None),
      adapterType = d.get('adapterType', None),
      isPublic = d.get('isPublic', None),
      handle = d.get('handle', None),
      description = d.get('description', None),
      dimensionality = d.get('dimensionality', None),
      limitAmount = d.get('limitAmount', None),
      limitUnit = d.get('limitUnit', None),
      apiKey = d.get('apiKey', None),
      metadata = d.get('metadata', None)
    )

@dataclass
class CreateModelRequest(NludbRequest):
  id: str = None
  name: str = None
  modelType: str = None
  url: str = None
  adapterType: str = None
  isPublic: bool = None
  handle: str = None
  description: str = None
  dimensionality: int = None
  limitAmount: int = None
  limitUnit: str = None
  apiKey: str = None
  metadata: str = None
  upsert: bool = None

@dataclass
class DeleteModelRequest(NludbRequest):
  modelId: str

@dataclass
class ListPublicModelsRequest(NludbRequest):
  modelType: str

@dataclass
class ListPrivateModelsRequest(NludbRequest):
  modelType: str

@dataclass
class ListModelsResponse(NludbRequest):
  models: List[Model]

  @staticmethod
  def safely_from_dict(d: any) -> "ListModelsResponse":
    return ListModelsResponse(
      models = [Model.safely_from_dict(x) for x in (d.get("models", []) or [])]
    )
