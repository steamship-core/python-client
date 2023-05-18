from abc import ABC
from typing import List, Optional

from pydantic import BaseModel

from steamship import Block
from steamship.agents.tool_data import ToolData


class Action(BaseModel, ABC):
    pass


class Tool(BaseModel):
    """The input to a ToolAction."""

    # The tool input may be an inlined list of blocks.
    inline_value: Optional[List[Block]]

    # The tool input may be the output of a known file.
    file_value: Optional[str]  # UUID

    # The tool input may be the output of a known task.
    tool_input_task: Optional[str]  # UUID


class ToolAction(BaseModel, ABC):
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

    output: ToolData
