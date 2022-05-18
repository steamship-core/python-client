from pydantic import BaseModel


class Request(BaseModel):
    pass


class GetRequest(Request):
    id: str = None
    handle: str = None
    upsert: bool = None


class IdentifierRequest(Request):
    id: str = None
    handle: str = None
