import logging
from typing import Tuple, List

from nludb import __version__
from nludb.types.base import Response
from nludb.base.base import ApiBase
from nludb.types.embedding import EmbedRequest, EmbedResponse, EmbedAndSearchRequest, EmbedAndSearchResponse
from nludb.types.embedding_index import IndexCreateRequest
from nludb.embedding_index import EmbeddingIndex
from nludb.classifier import Classifier
from nludb.types.file import File
from nludb.types.embedding_models import EmbeddingModels
from nludb.types.parsing import ParseRequest, ParseResponse, TokenMatcher, PhraseMatcher, DependencyMatcher
from nludb.types.parsing_models import ParsingModels
from nludb.types.tagging import TagRequest, TagResponse
from nludb.types.tagging_models import TaggingModels
from nludb.models import Models
from nludb.tasks import Tasks
from nludb.types.corpus import Corpus
from nludb.types.parsing import Doc

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

class NLUDB(ApiBase):
  """NLUDB Python Client."""

  def __init__(
    self, 
    api_key: str=None, 
    api_base: str=None,
    app_base: str=None,
    space_id: str=None,
    space_handle: str=None,
    profile: str=None,
    config_file: str=None,
    d_query: bool=False):
    super().__init__(
      api_key=api_key, 
      api_base=api_base,
      app_base=app_base,
      space_id=space_id,
      space_handle=space_handle,
      profile=profile,
      config_file=config_file,
      d_query=d_query)
    """
    The base class will properly detect and set the defaults. They should be None here.

    d_query is a Beta option that will return chainable responses, like:
      file.upload()
          .convert()
          .parse()
          .embed()
          .query()

    It offers no new functionality -- in fact at the moment it's slightly less in that you 
    are given the syntactically convenient response object for chaining rather than the actual
    response object of the invocation.
    """
    self.models = Models(self)
    self.tasks = Tasks(self)

  def create_corpus(
    self, 
    name: str,
    handle: str = None,
    description: str = None,
    externalId: str = None,
    externalType: str = None,
    metadata: any = None,
    isPublic: bool = False,
    upsert: bool = False,
    spaceId: bool = False,
    spaceHandle: bool = False
  ) -> Corpus:
    return Corpus.create(
      client=self,
      name=name,
      handle=handle,
      description=description,
      isPublic=isPublic,
      upsert=upsert,
      externalId=externalId,
      externalType=externalType,
      metadata=metadata,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def create_index(
    self, 
    name: str,
    model: str,
    upsert: bool = True,
    externalId: str = None,
    externalType: str = None,
    metadata: any = None,
    spaceId: str = None,
    spaceHandle: str = None
  ) -> EmbeddingIndex:
    return EmbeddingIndex.create(
      client=self,
      name=name,
      model=model,
      upsert=upsert,
      externalId=externalId,
      externalType=externalType,
      metadata=metadata,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def create_classifier(
    self, 
    name: str,
    model: str,
    upsert: bool = True,
    save: bool = None,
    labels: List[str] = None,
    spaceId: str = None,
    spaceHandle: str = None
  ) -> Classifier:
    return Classifier.create(
      client=self,
      model=model,
      name=name,
      upsert=upsert,
      save=save,
      labels=labels,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def upload(
    self,
    filename: str = None,
    name: str = None,
    content: str = None,
    format: str = None,
    convert: bool = False,
    spaceId: str = None,
    spaceHandle: str = None
  ) -> File:
    return File.upload(
      self,
      filename=filename,
      name=name,
      content=content,
      format=format,
      convert=convert,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def scrape(
    self,
    url: str,
    name: str = None,
    convert: bool = False,
    spaceId: str = None,
    spaceHandle: str = None
  ) -> File:
    if name is None:
      name = url
    return File.scrape(
      self,
      url,
      name,
      convert=convert,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def embed(
    self, 
    texts: List[str],
    model: str,
    spaceId: str = None,
    spaceHandle: str = None
  ) -> Response[EmbedResponse]:
    req = EmbedRequest(
      texts=texts,
      model=model
    )
    return self.post(
      'embedding/create',
      req,
      expect=EmbedResponse,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def embed_and_search(
    self, 
    query: str,
    docs: List[str],
    model: str,
    k: int = 1,
    spaceId: str = None,
    spaceHandle: str = None
  ) -> Response[EmbedAndSearchResponse]:
    req = EmbedAndSearchRequest(
      query=query,
      docs=docs,
      model=model,
      k=k
    )
    return self.post(
      'embedding/search',
      req,
      expect=EmbedAndSearchResponse,
      spaceId=spaceId,
      spaceHandle=spaceHandle
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
    metadata: any = None,
    spaceId: str = None,
    spaceHandle: str = None
  ) -> Response[ParseResponse]:
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
      expect=ParseResponse,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def tag(
    self,
    docs: List[Doc],
    model: str = ParsingModels.EN_DEFAULT,
    metadata: any = None,
    spaceId: str = None,
    spaceHandle: str = None
  ) -> Response[ParseResponse]:
    req = TagRequest(
      docs = docs,
      model = model,
      metadata = metadata
    )
    return self.post(
      'tagger/tag',
      req,
      expect=TagResponse,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )
