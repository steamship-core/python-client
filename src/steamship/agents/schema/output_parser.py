from abc import ABC, abstractmethod

from pydantic import BaseModel

from steamship.agents.schema.action import Action
from steamship.agents.schema.context import AgentContext


class OutputParser(BaseModel, ABC):
    """Used to convert text into Actions.

    Primarily used by LLM-based agents that generate textual descriptions of
    selected actions and their inputs. OutputParsers can be used to convert
    those descriptions into Action objects for the AgentService to run.

    Example:
     - input: "Action: GenerateImage
               ActionInput: row-house"
     - output: Action("dalle", "row-house")
    """

    @abstractmethod
    def parse(self, text: str, context: AgentContext) -> Action:
        """Convert text into an Action object."""
        pass
