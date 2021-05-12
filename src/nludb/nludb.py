import logging
from typing import Tuple, List

from nludb import __version__
from nludb.api.base import ApiBase
from nludb.types.embedding import EmbedRequest, EmbedResponse, EmbedAndSearchRequest, EmbedAndSearchResponse
from nludb.types.embedding_index import IndexCreateRequest
from nludb.embedding_index import EmbeddingIndex

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

class NLUDB(ApiBase):
  """NLUDB Client Library.

  """
  def __init__(
    self, 
    api_key: str=None, 
    api_domain: str="https://api.nludb.com/",
    api_version: int=1):
    super().__init__(api_key, api_domain, api_version)
 
  def create_index(
    self, 
    name: str,
    model: str,
    upsert: bool = True,
    externalId: str = None,
    externalType: str = None,
    metadata: any = None
  ) -> EmbeddingIndex:
    req = IndexCreateRequest(
      name=name,
      model=model,
      upsert=upsert,
      externalId=externalId,
      externalType=externalType,
      metadata=metadata,
    )
    res = self.post('embedding-index/create', req)
    return EmbeddingIndex(
      nludb=self,
      name=req.name,
      id=res.get("id", None)
    )

  def embed(
    self, 
    texts: List[str],
    model: str
  ) -> EmbedResponse:
    req = EmbedRequest(
      texts=texts,
      model=model
    )
    res = self.post('embedding/create', req)
    return EmbedResponse.safely_from_dict(res)

  def embed_and_search(
    self, 
    query: str,
    docs: List[str],
    model: str,
    k: int = 1
  ) -> EmbedAndSearchResponse:
    req = EmbedAndSearchRequest(
      query=query,
      docs=docs,
      model=model,
      k=k      
    )
    res = self.post('embedding/search', req)
    return EmbedAndSearchResponse.safely_from_dict(res)