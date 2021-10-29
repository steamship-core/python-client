import logging
import json
import re
from typing import Union, List, Dict, Tuple

from nludb import __version__
from nludb.api.base import ApiBase
from nludb.types.base import NludbResponse
from nludb.types.file import File
from nludb.types.corpus import *
from nludb.types.parsing_models import ParsingModels
from nludb.types.embedding_models import EmbeddingModels
from nludb.embedding_index import EmbeddingIndex
from nludb.types.embedding_index import IndexItem

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"

_logger = logging.getLogger(__name__)
  

class Corpus:
  """A corpus of files.
  """

  def __init__(self, nludb: ApiBase, createCorpusResponse: CreateCorpusResponse):
    self.nludb = nludb
    self._createCorpusResponse = createCorpusResponse
    self.id = createCorpusResponse.id
    self.name = createCorpusResponse.name
    self.handle = createCorpusResponse.handle
    self.isPublic = createCorpusResponse.isPublic

  def delete(self) -> NludbResponse[FileDeleteResponse]:
    req = DeleteCorpusRequest(
      corpusId=self.id
    )
    return self.nludb.post(
      'corpus/delete',
      req,
      expect=CreateCorpusResponse
    )

  def upload(
    self,
    nludb: ApiBase,
    filename: str = None,
    name: str = None,
    content: str = None,
    format: str = None,
    convert: bool = False
    ) -> File:

    return File.upload(
      nludb=self.nludb,
      corpus=self,
      filename=filename,
      name=name,
      content=content,
      format=format,
      convert=convert
    )

  def scrape(
    self,
    nludb: ApiBase,
    url: str,
    name: str = None,
    convert: bool = False) -> File:

    return File.scrape(
      nludb=self.nludb,
      corpus=self,
      url=url,
      name=name,
      convert=convert
    )
