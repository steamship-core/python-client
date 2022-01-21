from dataclasses import dataclass
from steamship.types.base import Request, Model
from steamship.client.base import ApiBase 


@dataclass
class GetRequest(Request):
  id: str = None
  name: str = None
  handle: str = None
  upsert: bool = None

@dataclass
class IdentifierRequest(Request):
  id: str
