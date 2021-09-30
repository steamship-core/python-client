import logging
from typing import Tuple, List

from nludb import __version__
from nludb.types.base import NludbResponse
from nludb.api.base import ApiBase
from nludb.types.embedding import EmbedRequest, EmbedResponse, EmbedAndSearchRequest, EmbedAndSearchResponse
from nludb.types.embedding_index import IndexCreateRequest
from nludb.embedding_index import EmbeddingIndex
from nludb.classifier import Classifier
from nludb.file import File
from nludb.types.embedding_models import EmbeddingModels
from nludb.types.parsing import ParseRequest, ParseResponse, TokenMatcher, PhraseMatcher, DependencyMatcher
from nludb.types.parsing_models import ParsingModels
from nludb.models import Models
from nludb.tasks import Tasks

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
    api_domain: str=None,
    api_version: int=None,):
    super().__init__(api_key, api_domain, api_version)
    """
    The base class will properly detect and set the defaults. They should be None here.
    """
    self.models = Models(self)
    self.tasks = Tasks(self)
 
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

  def create_classifier(
    self, 
    name: str,
    model: str,
    upsert: bool = True,
    save: bool = None,
    labels: List[str] = None
  ) -> Classifier:
    return Classifier.create(
      nludb=self,
      model=model,
      name=name,
      upsert=upsert,
      save=save,
      labels=labels
    )

  def upload_file(
    self,
    name: str,
    content: str,
    format: str = None,
    convert: bool = False
  ) -> File:
    return File.upload(
      self,
      name,
      content,
      format=format,
      convert=convert
    )

  def scrape_file(
    self,
    name: str,
    url: str,
    convert: bool = False
  ) -> File:
    return File.upload(
      self,
      name,
      url,
      convert=convert
    )

  def embed(
    self, 
    texts: List[str],
    model: str
  ) -> NludbResponse[EmbedResponse]:
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
  ) -> NludbResponse[EmbedAndSearchResponse]:
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
    includeTokens: bool = True,
    includeParseData: bool = True,
    includeEntities: bool = False,
    metadata: any = None
  ) -> NludbResponse[ParseResponse]:
    req = ParseRequest(
      docs = docs,
      model = model,
      tokenMatchers = tokenMatchers,
      phraseMatchers = phraseMatchers,
      dependencyMatchers = dependencyMatchers,
      includeTokens = includeTokens,
      includeParseData = includeParseData,
      includeEntities = includeEntities,
      metadata = metadata
    )
    return self.post(
      'parser/parse',
      req,
      expect=ParseResponse
    )

