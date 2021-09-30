import logging
import json
from typing import Union, List, Dict

from nludb import __version__
from nludb.api.base import ApiBase
from nludb.types.base import NludbResponse
from nludb.types.file import *
from nludb.types.parsing_models import ParsingModels

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
      id=res.fileId,
      format=res.fileFormat
    )

  @staticmethod
  def scrape(
    nludb: ApiBase,
    name: str,
    url: str,
    convert: bool = False) -> "File":
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
      id=res.fileId
    )

  def convert(self):
    req = FileConvertRequest(
      fileId=self.id
    )

    return self.nludb.post(
      'file/convert',
      payload=req,
      expect=FileConvertResponse,
      asynchronous=True
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
      asynchronous=True
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
