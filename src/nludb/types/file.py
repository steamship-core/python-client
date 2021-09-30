from typing import List
from dataclasses import dataclass
from nludb.types.base import NludbRequest, NludbResponseData
from nludb.types.parsing import DependencyMatcher, PhraseMatcher, TokenMatcher

class FileUploadType:
  file = "file"
  url = "url"

@dataclass
class FileUploadRequest(NludbRequest):
  type: str
  name: str
  fileFormat: str = None
  convert: bool = False

@dataclass
class FileUploadResponse(NludbResponseData):
  fileId: str
  fileFormat: str

  @staticmethod
  def safely_from_dict(d: any) -> "FileUploadResponse":
    return FileUploadResponse(
      fileId = d.get('fileId', None),
      fileFormat = d.get('fileFormat', None)
    )

@dataclass
class FileDeleteRequest(NludbRequest):
  fileId: str

@dataclass
class FileDeleteResponse(NludbResponseData):
  fileId: str

  @staticmethod
  def safely_from_dict(d: any) -> "FileDeleteResponse":
    return FileDeleteResponse(
      fileId = d.get('fileId', None)
    )

@dataclass
class FileConvertRequest(NludbRequest):
  fileId: str

@dataclass
class FileConvertResponse(NludbResponseData):
  fileId: str

  @staticmethod
  def safely_from_dict(d: any) -> "FileConvertResponse":
    return FileConvertResponse(
      fileId = d.get('fileId', None)
    )

@dataclass
class FileParseRequest(NludbRequest):
  fileId: str
  model: str = None
  tokenMatchers: List[TokenMatcher] = None
  phraseMatchers: List[PhraseMatcher] = None
  dependencyMatchers: List[DependencyMatcher] = None

@dataclass
class FileParseResponse(NludbResponseData):
  fileId: str

  @staticmethod
  def safely_from_dict(d: any) -> "FileParseResponse":
    return FileParseResponse(
      fileId = d.get('fileId', None)
    )

@dataclass
class Block(NludbRequest):
  blockId: str
  type: str
  value: str

  @staticmethod
  def safely_from_dict(d: any) -> "Block":
    return Block(
      blockId = d.get('blockId', None),
      type = d.get('type', None),
      value = d.get('value', None)
    )

@dataclass
class FileQueryRequest(NludbRequest):
  fileId: str
  blockType: str = None

@dataclass
class FileQueryResponse(NludbResponseData):
  fileId: str
  blocks: List[Block]

  @staticmethod
  def safely_from_dict(d: any) -> "FileQueryResponse":
    return FileQueryResponse(
      fileId = d.get('fileId', None),
      blocks = [Block.safely_from_dict(block) for block in d.get('blocks', None)]
    )
