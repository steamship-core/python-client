from pydantic import BaseModel

from steamship import Steamship


class AgentContext(BaseModel):
    client: Steamship
