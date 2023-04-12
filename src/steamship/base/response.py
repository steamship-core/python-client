from typing import Optional

from steamship.base.model import CamelModel


class Response(CamelModel):
    pass


class ListResponse(Response):
    next_page_token: Optional[str]
