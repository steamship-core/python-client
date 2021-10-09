import logging
import json
from typing import Union, List, Dict

from nludb import __version__
from nludb.api.base import ApiBase
from nludb.types.base import NludbResponse
from nludb.types.file import *
from nludb.types.parsing_models import ParsingModels
from nludb.types.embedding_models import EmbeddingModels
from nludb.embedding_index import EmbeddingIndex
from nludb.types.embedding_index import IndexItem

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

class File:
  """A file.
  """

  def __init__(self, nludb: ApiBase, id: str, name: str, format: str = None):
    self.nludb = nludb
    self.name = name
    self.id = id
    self.format = format

  def delete(self) -> NludbResponse[FileDeleteResponse]:
    req = FileDeleteRequest(
      self.id
    )
    return self.nludb.post(
      'file/delete',
      req,
      expect=FileDeleteResponse
    )

  def clear(self) -> NludbResponse[FileClearResponse]:
    req = FileClearRequest(
      self.id
    )
    return self.nludb.post(
      'file/clear',
      req,
      expect=FileClearResponse,
      if_d_query=self
    )

  @staticmethod
  def upload(
    nludb: ApiBase,
    name: str,
    content: str,
    format: str = None,
    convert: bool = False
    ) -> "File":
    req = FileUploadRequest(
      type=FileUploadType.file,
      name=name,
      fileFormat=format,
      convert=convert
    )

    res = nludb.post(
      'file/upload',
      payload=req,
      file=(name, content, "multipart/form-data"),
      expect=FileUploadResponse
    )

    return File(
      nludb=nludb,
      name=req.name,
      id=res.data.fileId,
      format=res.data.fileFormat
    )

  @staticmethod
  def scrape(
    nludb: ApiBase,
    url: str,
    name: str = None,
    convert: bool = False) -> "File":
    if name is None:
      name = url
    req = FileUploadRequest(
      type=FileUploadType.url,
      name=name,
      url=url,
      convert=convert
    )

    res = nludb.post(
      'file/upload',
      payload=req,
      expect=FileUploadResponse
    )

    return File(
      nludb=nludb,
      name=req.name,
      id=res.data.fileId
    )

  def convert(self, blockType: str = None, ocrModel: str = None):
    req = FileConvertRequest(
      fileId=self.id,
      blockType = blockType,
      ocrModel = ocrModel
    )

    return self.nludb.post(
      'file/convert',
      payload=req,
      expect=FileConvertResponse,
      asynchronous=True,
      if_d_query=self
    )

  def parse(
    self,
    model: str = ParsingModels.EN_DEFAULT,
    tokenMatchers: List[TokenMatcher] = None,
    phraseMatchers: List[PhraseMatcher] = None,
    dependencyMatchers: List[DependencyMatcher] = None
  ):
    req = FileParseRequest(
      fileId=self.id,
      model = model,
      tokenMatchers = tokenMatchers,
      phraseMatchers = phraseMatchers,
      dependencyMatchers = dependencyMatchers
    )

    return self.nludb.post(
      'file/parse',
      payload=req,
      expect=FileParseResponse,
      asynchronous=True,
      if_d_query=self
    )

  def query(self, blockType:str = None):
    req = FileQueryRequest(
      fileId=self.id,
      blockType=blockType
    )

    return self.nludb.post(
      'file/query',
      payload=req,
      expect=FileQueryResponse
    )

  def index(self, model:str = EmbeddingModels.QA, indexName: str = None, blockType: str = None, indexId: str = None, index: "EmbeddingIndex" = None, upsert: bool = True, reindex: bool = True) -> "EmbeddingIndex":
    # TODO: This should really be done all on the server, but for now we'll do it in the client
    # to facilitate demos.

    if indexId is None and index is not None:
      indexId = index.id
    
    if indexName is None:
      indexName = "{}-{}".format(self.id, model)

    if indexId is None and index is None:
      index = self.nludb.create_index(
        name=indexName,
        model=model,
        upsert=True,
      )
    elif index is None:
      index = EmbeddingIndex(
        nludb=self.nludb, 
        indexId = indexId
      )
    
    # We have an index available to us now. Perform the query.
    blocks = self.query(blockType = blockType).data.blocks

    items = []
    for block in blocks:
      item = IndexItem(
        value=block.value,
        externalId=block.blockId,
        externalType="block"
      )
      items.append(item)
    
    insert_task = index.insert_many(items, reindex=reindex)

    if self.nludb.d_query:
      insert_task.wait()
      return index
    return insert_task

  def raw(self):
    req = FileRawRequest(
      fileId=self.id,
    )

    return self.nludb.post(
      'file/raw',
      payload=req
    )
