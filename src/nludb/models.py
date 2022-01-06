import logging
import json
from typing import Union, List, Dict

from nludb import __version__
from nludb.api.base import ApiBase, Response
from nludb.types.model import *

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

class Models:
  """A persistent, read-optimized index over embeddings.
  """

  def __init__(self, client: ApiBase):
    self.client = client
  
  def create(
    self, 
    name: str,
    description: str,
    modelType: str,
    url: str,
    adapterType: str,
    isPublic: bool,
    handle: str = None,
    dimensionality: int = None,
    limitAmount: int = None,
    limitUnit: str = None,
    apiKey: str = None,
    metadata: Union[str, Dict, List] = None,
    upsert: bool = None,
    spaceId: str = None,
    spaceHandle: str = None
  ) -> Response[Model]:
    
    if isinstance(metadata, dict) or isinstance(metadata, list):
      metadata = json.dumps(metadata)

    req = CreateModelRequest(
      name=name,
      modelType=modelType,
      url=url,
      adapterType=adapterType,
      isPublic=isPublic,
      handle=handle,
      description=description,
      dimensionality=dimensionality,
      limitAmount=limitAmount,
      limitUnit=limitUnit,
      apiKey=apiKey,
      metadata=metadata,
      upsert=upsert
    )
    return self.client.post(
      'model/create',
      req,
      expect=Model,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def listPublic(
    self,
    modelType: str = None,
    spaceId: str = None,
    spaceHandle: str = None
  ) -> Response[ListModelsResponse]:
    return self.client.post(
      'model/public',
      ListPublicModelsRequest(modelType=modelType),
      expect=ListModelsResponse,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def listPrivate(
    self,
    modelType = None,
    spaceId: str = None,
    spaceHandle: str = None
  ) -> Response[ListModelsResponse]:
    return self.client.post(
      'model/private',
      ListPrivateModelsRequest(modelType=modelType),
      expect=ListModelsResponse,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def delete(
    self,
    id,
    spaceId: str = None,
    spaceHandle: str = None
  ) -> Response[Model]:
    return self.client.post(
      'model/delete',
      DeleteModelRequest(modelId=id),
      expect=Model,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )
