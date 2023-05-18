from abc import ABC
from typing import Optional

from pydantic import BaseModel

from steamship.agents.tool_data import ToolData


class Action(BaseModel, ABC):
    pass


class ToolAction(BaseModel):
    """Represents the application of a Tool to a sequence of Blocks."""

    # DATA DEPENDENCIES
    # -----------------

    # The tool that produced the input. To support using the tool's post-processor
    input_tool_name: Optional[str] = None
    # The actual input
    input: ToolData

    # EXECUTION
    # ---------

    tool_name: str

    # OUTPUT
    # ------

    output: Optional[ToolData] = None
