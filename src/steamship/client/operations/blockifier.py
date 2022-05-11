from pydantic import BaseModel


class BlockifyRequest(BaseModel):
    type: str = None
    pluginInstance: str = None
    id: str = None
    handle: str = None
    name: str = None
