from abc import ABC

from steamship import Steamship
from steamship.agents.tools.tool import Tool


class WorkspaceTool(Tool, ABC):
    client: Steamship
