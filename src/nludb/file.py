import logging
import json
from typing import Union, List, Dict

from nludb import __version__
from nludb.api.base import ApiBase
from nludb.types.file import *

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

class File:
  """A file.
  """

  def __init__(self, nludb: ApiBase, id: str, name: str):
    self.nludb = nludb
    self.name = name
    self.id = id

  def delete(self) -> FileDeleteResponse:
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
    content: str) -> "File":
    req = FileUploadRequest(
      type=FileUploadType.file,
      name=name,
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
      id=res.fileId
    )

  @staticmethod
  def scrape(
    nludb: ApiBase,
    name: str,
    url: str) -> "File":
    req = FileUploadRequest(
      type=FileUploadType.url,
      name=name,
      url=url
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

  def query(self):
    req = FileQueryRequest(
      fileId=self.id
    )

    return self.nludb.post(
      'file/query',
      payload=req,
      expect=FileQueryResponse
    )
