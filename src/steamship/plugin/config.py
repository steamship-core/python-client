from pydantic import BaseModel

class Config(BaseModel):
    """Base class for a Steamship Plugin's configuration object."""
    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v}
        super().__init__(**kwargs)
