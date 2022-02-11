from dataclasses import dataclass


class Request:
    pass


@dataclass
class GetRequest(Request):
    id: str = None
    name: str = None
    handle: str = None
    upsert: bool = None


@dataclass
class IdentifierRequest(Request):
    id: str = None
    handle: str = None
