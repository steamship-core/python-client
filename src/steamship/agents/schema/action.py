from typing import List, Optional

from pydantic import BaseModel
from pydantic.fields import Field

from steamship import Block


class Action(BaseModel):
    """Actions represent a binding of a Tool to the inputs supplied to the tool.

    Upon completion, the Action also contains the output of the Tool given the inputs.
    """

    tool: str
    """Name of tool used by this action."""

    input: List[Block]
    """Data provided directly to the Tool (full context is passed in run)."""

    output: Optional[List[Block]]
    """Any direct output produced by the Tool."""

    is_final: bool = Field(default=False)
    """Whether this Action should be the final action performed in a reasoning loop.

    Setting this to True means that the executing Agent should halt any reasoning.
    """


class FinishAction(Action):
    """Represents a final selected action in an Agent Execution."""

    tool = "Agent-FinishAction"
    input: List[Block] = []
    is_final = True
