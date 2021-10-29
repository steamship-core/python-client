import logging
import json
import re
from typing import Union, List, Dict, Tuple

from nludb import __version__
from nludb.api.base import ApiBase
from nludb.types.base import NludbResponse
from nludb.file import File
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
    self.id = createCorpusResponse.corpusId
    self.name = createCorpusResponse.name
    self.handle = createCorpusResponse.handle
    self.isPublic = createCorpusResponse.isPublic

  @staticmethod
  def create(
    nludb: ApiBase,
    name: str,
    handle: str = None,
    description: str = None,
    externalId: str = None,
    externalType: str = None,
    metadata: any = None,
    isPublic: bool = False,
    upsert: bool = True
  ) -> "Corpus":
    if isinstance(metadata, dict) or isinstance(metadata, list):
      metadata = json.dumps(metadata)

    req = CreateCorpusRequest(
      name=name,
      handle=handle,
      description=description,
      isPublic=isPublic,
      upsert=upsert,
      externalId=externalId,
      externalType=externalType,
      metadata=metadata
    )
    res = nludb.post('corpus/create', req, expect=CreateCorpusResponse)
    return Corpus(
      nludb=nludb,
      createCorpusResponse=res.data
    )
    
  def delete(self) -> NludbResponse[CreateCorpusResponse]:
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
    filename: str = None,
    name: str = None,
    content: str = None,
    format: str = None,
    convert: bool = False
    ) -> File:

    return File.upload(
      nludb=self.nludb,
      corpusId=self.id,
      filename=filename,
      name=name,
      content=content,
      format=format,
      convert=convert
    )

  def scrape(
    self,
    url: str,
    name: str = None,
    convert: bool = False) -> File:

    return File.scrape(
      nludb=self.nludb,
      corpusId=self.id,
      url=url,
      name=name,
      convert=convert
    )
