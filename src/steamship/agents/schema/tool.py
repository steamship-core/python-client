from abc import abstractmethod
from typing import Any, List, Union

from pydantic.main import BaseModel

from steamship import Block, Task
from steamship.agents.schema.functions import (
    FunctionParameters,
    FunctionProperty,
    JSONType,
    OpenAIFunction,
)


class AgentContext(BaseModel):
    """Placeholder to avoid circular dependency."""

    # TODO(doug): refactor so this is not necessary
    pass


class Tool(BaseModel):
    """Tools provide functionality that may be used by `AgentServices`, as directed by `Agents`, to
    achieve a goal.

    Tools may be used to wrap Steamship packages and plugins, as well as third-party backend services,
    and even locally-contained bits of Python code.
    """

    name: str
    """The short name for the tool.
    This will be used by Agents to refer to this tool during action selection."""

    agent_description: str
    """Description for use in an agent in order to enable Action selection.
    It should include a short summary of what the Tool does, what the inputs to the Tool should be,
    and what the outputs of the tool are."""

    human_description: str
    """Human-friendly description.
    Used for logging, tool indices, etc."""

    return_direct: bool = False
    """Whether to return the tool's output directly.

    Setting this to True means that after the tool is called, the AgentExecutor will stop looping.
    """

    @abstractmethod
    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Task[Any]]:
        """Run the tool given the provided input and context.

        At the moment, only synchronous Tools (those that return List[Block]) are supported.

        Support for asynchronous Tools (those that return Task[Any]) will be added shortly.
        """
        raise NotImplementedError()

    def post_process(self, async_task: Task, context: AgentContext) -> List[Block]:
        """Transforms Task output into a List[Block]."""
        pass

    def as_openai_function(self) -> OpenAIFunction:
        text_property_schema = FunctionProperty(
            type=JSONType.string,
            description="text prompt for a function.",
        )

        uuid_property_schema = FunctionProperty(
            type=JSONType.string,
            description="UUID for a Steamship Block. Used to refer to a non-textual input generated by another "
            'function. Example: "c2f6818c-233d-4426-9dc5-f3c28fa33068"',
        )

        params = FunctionParameters(
            properties={"text": text_property_schema, "uuid": uuid_property_schema},
        )

        return OpenAIFunction(
            name=self.name,
            description=self.human_description,
            parameters=params,
        )
