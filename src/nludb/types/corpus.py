import json
from typing import Any, List
from dataclasses import dataclass
from nludb.types.base import Request, Model, Response, str_to_metadata
from nludb.api.base import ApiBase
from nludb.types.file import File, ListFilesResponse

@dataclass
class CreateCorpusRequest(Request):
  corpusId: str = None
  name: str = None
  handle: str = None
  description: str = None
  externalId: str = None
  externalType: str = None
  isPublic: bool = None
  metadata: str = None
  upsert: bool = None

@dataclass
class DeleteCorpusRequest(Request):
  corpusId: str

@dataclass
class ListPublicCorporaRequest(Request):
  pass

@dataclass
class ListPrivateCorporaRequest(Request):
  pass

@dataclass
class Corpus(Model):
  """A corpus of files.
  """
  id: str = None
  name: str = None
  handle: str = None
  description: str = None
  externalId: str = None
  externalType: str = None
  metadata: Any = None

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "Corpus":
    return Corpus(
      client = client,
      id = d.get('id', None),
      name = d.get('name', None),
      handle = d.get('handle', None),
      description = d.get('description', None),
      externalId = d.get('externalId', None),
      externalType = d.get('externalType', None),
      metadata = str_to_metadata(d.get("metadata", None)),
    )

  @staticmethod
  def create(
    client: ApiBase,
    name: str,
    handle: str = None,
    description: str = None,
    externalId: str = None,
    externalType: str = None,
    metadata: any = None,
    isPublic: bool = False,
    upsert: bool = True,
    spaceId: str = None,
    spaceHandle: str = None
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
    return client.post(
      'corpus/create',
      req, 
      expect=Corpus,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )
    
  def delete(
    self,
    spaceId: str = None,
    spaceHandle: str = None) -> Response["Corpus"]:
    req = DeleteCorpusRequest(
      corpusId=self.id
    )
    return self.client.post(
      'corpus/delete',
      req,
      expect=Corpus,
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
      client=self.client,
      corpusId=self.id,
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
    spaceHandle: str = None) -> File:

    return File.scrape(
      client=self.client,
      corpusId=self.id,
      url=url,
      name=name,
      convert=convert,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def list_files(
    self,
    spaceId: str = None,
    spaceHandle: str = None) -> ListFilesResponse:
    return File.list(
      client=self.client,
      corpusId=self.id,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

@dataclass
class ListCorporaResponse(Request):
  corpora: List[Corpus]

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "ListCorporaResponse":
    return ListCorporaResponse(
      models = [Corpus.safely_from_dict(x) for x in (d.get("corpus", []) or [])]
    )
