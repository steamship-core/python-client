from typing import Callable

from steamship.agents.action import ToolAction


class AgentContext:
    invoke_tool: Callable[[ToolAction], ToolAction]
