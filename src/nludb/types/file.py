import logging
import json
import re

from nludb import __version__
from typing import Union, List, Dict, Tuple
from typing import List
from dataclasses import dataclass
from nludb.client.base import ApiBase
from nludb.base.requests import IdentifierRequest
from nludb.types.base import Request, Response, Response
from nludb.types.conversion import ConvertRequest, ConvertResponse
from nludb.types.block import Block
from nludb.types.model import ModelTargetType
from nludb.types.parsing import DependencyMatcher, ParseRequest, PhraseMatcher, TokenMatcher, ParseResponse
from nludb.types.parsing_models import ParsingModels
from nludb.types.embedding_models import EmbeddingModels
from nludb.types.tag import *
from nludb.types.embedding_index import EmbeddingIndex
from nludb.types.embedding_index import IndexItem
from nludb.types.tag import TagObjectRequest

class FileUploadType:
  file = "file"
  url = "url"

_logger = logging.getLogger(__name__)

def parseDquery(query: str) -> List[Tuple[str, str, str]]:
  query = re.sub(' +', ' ', query.strip())
  parts = re.split(r'\s*(?=[@#])', query)
  ret = []

  for s in parts:
    s = s.strip()
    if not s:
      continue

    command = ''
    if s[0] in ['@', '#']:
      command = s[0]
      s = s[1:]
    
    if command == '':
      ret.append((command, None, s))
      continue

    if '"' not in s and ":" not in s:
      if command == '#':
        ret.append((command, 'contains', s))
      else:
        ret.append((command, s, None))
      continue

    modifier = None
    if ':' in s:
      ss = s.split(':')
      modifier = ss[0]
      s = ss[1]
    
    content = s
    if '"' in s:
      i = s.index('"')
      content = s[1+i:-1]
      if modifier is None:
        s = s[:i]
        modifier = s
        if modifier == '':
          modifier = None
    
    ret.append((command, modifier, content))
  return ret
  
@dataclass
class FileUploadRequest(Request):
  type: str
  corpusId: str = None
  name: str = None
  url: str = None
  mimeType: str = None
  convert: bool = False

@dataclass
class FileClearResponse(Model):
  id: str

@dataclass
class FileTagRequest(Request):
  id: str
  model: str = None

@dataclass
class FileTagResponse(Model):
  id: str
  tagResult: ParseResponse

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "FileTagResponse":
    return FileTagResponse(
      id = d.get('id', None),
      tagResult = ParseResponse.safely_from_dict(d.get('tagResult', {}), client=client)
    )

@dataclass
class SpanQuery:
  text: str = None
  label: str = None
  spanType: str = None

@dataclass
class FileQueryRequest(Request):
  fileId: str
  type: str = None
  hasSpans: List[SpanQuery] = None
  text: str = None
  textMode: str = None
  isQuote: bool = None

@dataclass
class FileQueryResponse(Model):
  id: str
  blocks: List[Block]

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "FileQueryResponse":
    return FileQueryResponse(
      id = d.get('id', None),
      blocks = [Block.safely_from_dict(block, client=client) for block in d.get('blocks', None)]
    )

@dataclass
class FileRawRequest(Request):
  id: str

@dataclass
class ListFilesRequest(Request):
  corpusId: str = None

@dataclass
class ListFilesResponse(Model):
  files: List["File"]

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "ListFilesResponse":
    return ListFilesResponse(
      files = [File.safely_from_dict(f, client = client) for f in d.get('files', [])]
    )

@dataclass
class File(Model):
  """A file.
  """
  client: ApiBase = None
  id: str = None
  name: str = None
  handle: str = None
  mimeType: str = None
  spaceId: str = None
  corpusId: str = None

  
  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "File":
    return File(
      client=client,
      id=d.get('id', None),
      handle=d.get('handle', None),
      name=d.get('name', None),
      mimeType=d.get('mimeType', None),
      corpusId=d.get('corpusId', None),
      spaceId=d.get('spaceId', None)
    )

  def delete(
    self,
    spaceId: str = None,
    spaceHandle: str = None,
    space: any = None) -> "Response[File]":
    return self.client.post(
      'file/delete',
      IdentifierRequest(id=self.id),
      expect=File,
      spaceId=spaceId,
      spaceHandle=spaceHandle,
      space=space
    )

  def clear(
    self,
    spaceId: str = None,
    spaceHandle: str = None,
    space: any = None) -> Response[FileClearResponse]:
    return self.client.post(
      'file/clear',
      IdentifierRequest(id=self.id),
      expect=FileClearResponse,
      if_d_query=self,
      spaceId=spaceId,
      spaceHandle=spaceHandle,
      space=space
    )

  @staticmethod
  def upload(
    client: ApiBase,
    filename: str = None,
    name: str = None,
    content: str = None,
    mimeType: str = None,
    corpusId: str = None,
    convert: bool = False,
    spaceId: str = None,
    spaceHandle: str = None,
    space: any = None
    ) -> "Response[File]":

    if filename is None and name is None and content is None:
      raise Exception("Either filename or name + content must be provided.")
    
    if filename is not None:
      with open(filename, 'rb') as f:
        content = f.read()
        name = filename

    req = FileUploadRequest(
      type=FileUploadType.file,
      corpusId=corpusId,
      name=name,
      mimeType=mimeType,
      convert=convert
    )

    return client.post(
      'file/create',
      payload=req,
      file=(name, content, "multipart/form-data"),
      expect=File,
      spaceId=spaceId,
      spaceHandle=spaceHandle,
      space=space
    )

  @staticmethod
  def list(
    client: ApiBase,
    corpusId: str = None,
    spaceId: str = None,
    spaceHandle: str = None,
    space: any = None
  ):
    req = ListFilesRequest(
      corpusId=corpusId
    )
    res = client.post(
      'file/list',
      payload=req,
      expect=ListFilesResponse,
      spaceId=spaceId,
      spaceHandle=spaceHandle,
      space=space
    ) 
    return res

  @staticmethod
  def scrape(
    client: ApiBase,
    url: str,
    name: str = None,
    corpusId: str = None,
    convert: bool = False,
    spaceId: str = None,
    spaceHandle: str = None,
    space: any = None) -> "File":
    if name is None:
      name = url
    req = FileUploadRequest(
      type=FileUploadType.url,
      name=name,
      url=url,
      corpusId=corpusId,
      convert=convert
    )

    return client.post(
      'file/create',
      payload=req,
      expect=File,
      spaceId=spaceId,
      spaceHandle=spaceHandle,
      space=space
    )

  def convert(
    self, 
    model: str = None, 
    spaceId: str = None,
    spaceHandle: str = None,
    space: any = None):
    req = ConvertRequest(
      id=self.id,
      type=ModelTargetType.file,
      model=model
    )

    return self.client.post(
      'model/convert',
      payload=req,
      expect=ConvertResponse,
      asynchronous=True,
      if_d_query=self,
      spaceId=spaceId,
      spaceHandle=spaceHandle,
      space=space
    )

  def parse(
    self,
    model: str = ParsingModels.EN_DEFAULT,
    tokenMatchers: List[TokenMatcher] = None,
    phraseMatchers: List[PhraseMatcher] = None,
    dependencyMatchers: List[DependencyMatcher] = None,
    spaceId: str = None,
    spaceHandle: str = None,
    space: any = None
  ):
    req = ParseRequest(
      type=ModelTargetType.file,
      id=self.id,
      model = model,
      tokenMatchers = tokenMatchers,
      phraseMatchers = phraseMatchers,
      dependencyMatchers = dependencyMatchers
    )

    return self.client.post(
      'model/parse',
      payload=req,
      expect=ParseResponse,
      asynchronous=True,
      if_d_query=self,
      spaceId=spaceId,
      spaceHandle=spaceHandle,
      space=space
    )

  def tag(
    self,
    model: str = ParsingModels.EN_DEFAULT,
    spaceId: str = None,
    spaceHandle: str = None,
    space: any = None
  ):
    req = FileTagRequest(
      id=self.id,
      model = model
    )

    return self.client.post(
      'file/tag',
      payload=req,
      expect=FileTagResponse,
      asynchronous=True,
      spaceId=spaceId,
      spaceHandle=spaceHandle,
      space=space
    )

  def dquery(
    self, 
    dQuery: str,
    spaceId: str = None,
    spaceHandle: str = None,
    space: any = None):
    blockType = None
    hasSpans = []
    text = None
    isQuote = None
    textMode = None

    for tup in parseDquery(dQuery):
      (cmd, subcmd, content) = tup
      if cmd == '':
        blockType = content
      elif cmd == '#':
        text = content
        textMode = subcmd
      elif cmd == '@':
        hasSpans.append(SpanQuery(label=subcmd, text=content))

    return self.query(
      blockType=blockType, 
      hasSpans=hasSpans,
      text=text,
      textMode=textMode,
      isQuote=isQuote,
      pd=True,
      spaceId=spaceId,
      spaceHandle=spaceHandle,
      space=space
    )

  def query(
    self, 
    blockType:str = None, 
    hasSpans: List[SpanQuery] = None,
    text: str = None,
    textMode: str = None,
    isQuote: bool = None,
    pd: bool = False,
    spaceId: str = None,
    spaceHandle: str = None,
    space: any = None
    ):

    req = FileQueryRequest(
      fileId=self.id,
      type=blockType,
      hasSpans=hasSpans,
      text=text,
      textMode=textMode,
      isQuote=isQuote
    )

    res = self.client.post(
      'file/query',
      payload=req,
      expect=FileQueryResponse,
      spaceId=spaceId,
      spaceHandle=spaceHandle,
      space=space
    )
    if not self.client.d_query:
      return res
    else:
      if pd is False:
        return res.data.blocks
      else:
        import pandas as pd # type: ignore   
        return pd.DataFrame([(block.type, block.value) for block in res.data.blocks], columns =['Type', 'Value'])


  def index(
    self, 
    model:str = EmbeddingModels.QA, 
    indexName: str = None, 
    blockType: str = None, 
    indexId: str = None, 
    index: "EmbeddingIndex" = None, 
    upsert: bool = True, 
    reindex: bool = True,
    spaceId: str = None,
    spaceHandle: str = None,
    space: any = None) -> "EmbeddingIndex":
    # TODO: This should really be done all on the server, but for now we'll do it in the client
    # to facilitate demos.

    if indexId is None and index is not None:
      indexId = index.id
    
    if indexName is None:
      indexName = "{}-{}".format(self.id, model)

    if indexId is None and index is None:
      index = self.client.create_index(
        name=indexName,
        model=model,
        upsert=True,
        spaceId=spaceId,
        spaceHandle=spaceHandle,
        space=space
      )
    elif index is None:
      index = EmbeddingIndex(
        client=self.client, 
        indexId = indexId
      )
    
    # We have an index available to us now. Perform the query.
    blocks = self.query(
      blockType = blockType,
      spaceId=spaceId,
      spaceHandle=spaceHandle,
      space=space      
    )
    if not self.client.d_query:
      blocks = blocks.data.blocks

    items = []
    for block in blocks:
      item = IndexItem(
        value=block.value,
        externalId=block.blockId,
        externalType="block"
      )
      items.append(item)
    
    insert_task = index.insert_many(
      items, 
      reindex=reindex,
      spaceId=spaceId,
      spaceHandle=spaceHandle,
      space=space
    )

    if self.client.d_query:
      insert_task.wait()
      return index
    return insert_task

  def raw(
    self,
    spaceId: str = None,
    spaceHandle: str = None,
    space: any = None):
    req = FileRawRequest(
      id=self.id,
    )

    return self.client.post(
      'file/raw',
      payload=req,
      spaceId=spaceId,
      spaceHandle=spaceHandle,
      space=space,
      rawResponse=True
    )

  def add_tags(
    self, 
    tags = List[Union[str, CreateTagRequest]],
    spaceId: str = None,
    spaceHandle: str = None,
    space: any = None):
    tagsNew = []
    for tag in tags:
      if type(tag) == str:
        tagsNew.append(CreateTagRequest(name=tag, upsert=True))
      elif type(tag) == CreateTagRequest:
        tagsNew.append(tag)
      else:
        raise(Exception("Unable to add tag of type: {}".format(type(tag))))

    req = TagObjectRequest(
      tags = tagsNew,
      objectType='File',
      objectId = self.id
    )

    return self.client.post(
      'tag/create',
      payload=req,
      expect=TagObjectRequest,
      spaceId=spaceId,
      spaceHandle=spaceHandle,
      space=space
    )

  def remove_tags(
    self, 
    tags = List[Union[str, DeleteTagRequest]],
    spaceId: str = None,
    spaceHandle: str = None,
    space: any = None):
    tagsNew = []
    for tag in tags:
      if type(tag) == str:
        tagsNew.append(DeleteTagRequest(name=tag))
      elif type(tag) == DeleteTagRequest:
        tagsNew.append(tag)
      else:
        raise(Exception("Unable to remove tag of type: {}".format(type(tag))))

    req = TagObjectRequest(
      tags = tagsNew,
      objectType='File',
      objectId = self.id
    )

    return self.client.post(
      'tag/delete',
      payload=req,
      expect=TagObjectRequest,
      spaceId=spaceId,
      spaceHandle=spaceHandle,
      space=space
    )

  def list_tags(
    self,
    spaceId: str = None,
    spaceHandle: str = None,
    space: any = None):
    req = ListTagsRequest(
      objectType='File',
      objectId = self.id
    )

    return self.client.post(
      'tag/list',
      payload=req,
      expect=TagObjectRequest,
      spaceId=spaceId,
      spaceHandle=spaceHandle,
      space=space
    )