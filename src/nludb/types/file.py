from typing import List
from dataclasses import dataclass
from nludb.types.base import NludbRequest, NludbResponse

class FileUploadType:
  file = "file"
  url = "url"

@dataclass
class FileUploadRequest(NludbRequest):
  type: str
  name: str
  convert: bool = False

@dataclass
class FileUploadResponse(NludbResponse):
  fileId: str

  @staticmethod
  def safely_from_dict(d: any) -> "FileUploadResponse":
    return FileUploadResponse(
      fileId = d.get('fileId', None)
    )

@dataclass
class FileDeleteRequest(NludbRequest):
  fileId: str

@dataclass
class FileDeleteResponse(NludbResponse):
  fileId: str

  @staticmethod
  def safely_from_dict(d: any) -> "FileDeleteResponse":
    return FileDeleteResponse(
      fileId = d.get('fileId', None)
    )

