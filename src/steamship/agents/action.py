import abc
from typing import List

from pydantic import BaseModel

from steamship import Block


@abc.ABC
class Action(BaseModel):
    pass


class SpeakAction(Action):
    """Represents saying something to the chat."""

    messages: List[Block]


class ToolAction(Action):
    """Represents the invocation of a Tool."""

    tool_name: str
    tool_input: List[Block]


class NoOpAction(Action):
    """Represents no action."""

    pass


class FinishAction(Action):
    """Represents the cessasation of auto-reasoning loop."""

    messages: List[Block]
