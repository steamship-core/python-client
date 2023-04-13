from enum import Enum
from typing import Optional

from steamship.base.model import CamelModel


class Request(CamelModel):
    pass


class GetRequest(Request):
    id: str = None
    handle: str = None


class CreateRequest(Request):
    id: str = None
    handle: str = None


class UpdateRequest(Request):
    id: str = None
    handle: str = None


class IdentifierRequest(Request):
    id: str = None
    handle: str = None


class SortOrder(str, Enum):
    ASC = "ASC"
    DESC = "DESC"


class ListRequest(Request):
    page_size: Optional[int]
    page_token: Optional[str]
    sort_order: Optional[SortOrder] = SortOrder.DESC


class DeleteRequest(Request):
    id: str
