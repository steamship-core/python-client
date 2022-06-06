from pydantic import BaseModel


class Config(BaseModel):
    """Base class for a Steamship Plugin's configuration object."""

    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        super().__init__(**kwargs)
