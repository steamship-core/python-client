from steamship.base.configuration import CamelModel


class Request(CamelModel):
    class Config:
        use_enum_values = True


class GetRequest(Request):
    id: str = None
    handle: str = None
    upsert: bool = None


class IdentifierRequest(Request):
    id: str = None
    handle: str = None
