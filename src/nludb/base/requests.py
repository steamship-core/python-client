from dataclasses import dataclass
from nludb.types.base import Request, Model
from nludb.base.base import ApiBase 


@dataclass
class GetRequest(Request):
  id: str = None
  name: str = None
  handle: str = None
  upsert: bool = None

@dataclass
class DeleteRequest(Request):
  id: str
