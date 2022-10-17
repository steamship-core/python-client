from steamship.base.model import CamelModel


class Request(CamelModel):
    pass


class GetRequest(Request):
    id: str = None
    handle: str = None
    upsert: bool = None


class CreateRequest(Request):
    id: str = None
    handle: str = None
    upsert: bool = None


class IdentifierRequest(Request):
    id: str = None
    handle: str = None


class ListRequest(Request):
    pass


class DeleteRequest(Request):
    id: str
