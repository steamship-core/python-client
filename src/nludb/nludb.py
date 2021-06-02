import logging
from typing import Tuple, List

from nludb import __version__
from nludb.api.base import ApiBase
from nludb.types.embedding import EmbedRequest, EmbedResponse, EmbedAndSearchRequest, EmbedAndSearchResponse
from nludb.types.embedding_index import IndexCreateRequest
from nludb.embedding_index import EmbeddingIndex
from nludb.file import File
from nludb.types.file import FileUploadRequest, FileUploadResponse
from nludb.types.parsing import ParseRequest, ParseResponse, TokenMatcher, PhraseMatcher, DependencyMatcher
from nludb.types.parsing_models import ParsingModels

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
    return EmbeddingIndex.create(
      nludb=self,
      name=name,
      model=model,
      upsert=upsert,
      externalId=externalId,
      externalType=externalType,
      metadata=metadata
    )

  def upload_file(
    self,
    name: str,
    content: str
  ) -> File:
    return File.upload(
      self,
      name,
      content
    )

  def scrape_file(
    self,
    name: str,
    url: str
  ) -> File:
    return File.upload(
      self,
      name,
      url
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
    return self.post(
      'embedding/create',
      req,
      expect=EmbedResponse
    )

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
    return self.post(
      'embedding/search',
      req,
      expect=EmbedAndSearchResponse
    )

  def parse(
    self,
    docs: List[str],
    model: str = ParsingModels.EN_DEFAULT,
    tokenMatchers: List[TokenMatcher] = None,
    phraseMatchers: List[PhraseMatcher] = None,
    dependencyMatchers: List[DependencyMatcher] = None,
  ) -> ParseResponse:
    req = ParseRequest(
      docs = docs,
      model = model,
      tokenMatchers = tokenMatchers,
      phraseMatchers = phraseMatchers,
      dependencyMatchers = dependencyMatchers
    )
    return self.post(
      'parser/parse',
      req,
      expect=ParseResponse
    )
