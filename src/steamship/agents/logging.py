from pydantic.fields import Field
from pydantic.main import BaseModel


class AgentLogging:
    """These keys are for use in the `extra` field of agent logging operations. #noqa: RST203

    For now, they are manually applied at the time of logging. In the future, the AgentContext may provide a logger
    which fills some automatically.

    For example:

    logging.info("I should use tool MakeAPicture", extra={
        AgentLogging.AGENT_NAME: self.name,
        AgentLogging.IS_AGENT_MESSAGE: True,
        AgentLogging.MESSAGE_TYPE: AgentLogging.THOUGHT
    }) # noqa: RST203

    This provides:

    * Structured additions to Fluent/Elastic that help with internal debugging.
    * Helpful output in development mode
    * [Eventual] User-visible logs
    * [Eventual] Visualiations about tool execution and ReAct reasoning

    """

    AGENT_NAME = "agent_name"
    TOOL_NAME = "tool_name"
    LLM_NAME = "llm_name"
    IS_MESSAGE = "is_message"

    MESSAGE_TYPE = "agent_message_type"
    THOUGHT = "thought"
    OBSERVATION = "observation"
    ACTION = "action"
    MESSAGE = "message"
    PROMPT = "prompt"

    MESSAGE_AUTHOR = "message_author"
    USER = "user"
    AGENT = "agent"
    TOOL = "tool"
    SYSTEM = "system"
    LLM = "llm"


LOGGING_FORMAT = {
    "level": "%(levelname)s",
    "host": "%(hostname)s",
    "where": "%(module)s.%(filename)s.%(funcName)s:%(lineno)s",
    "type": "%(levelname)s",
    "stack_trace": "%(exc_text)s",
    "message_type": "%(message_type)s",
    "component_name": "%(component_name)s",
    AgentLogging.IS_MESSAGE: f"%({AgentLogging.IS_MESSAGE})s",  # b doesn't work. Unsure how to make a bool
    AgentLogging.AGENT_NAME: f"%({AgentLogging.AGENT_NAME})s",
    AgentLogging.MESSAGE_AUTHOR: f"%({AgentLogging.MESSAGE_AUTHOR})s",
    AgentLogging.MESSAGE_TYPE: f"%({AgentLogging.MESSAGE_TYPE})s",
    AgentLogging.TOOL_NAME: f"%({AgentLogging.TOOL_NAME})s",
}


class StreamingOpts(BaseModel):
    """Controls what status messages for a given AgentService invocation should be included in the resultant stream."""

    include_agent_messages: bool = Field(default=True)
    """Whether or not to include agent-generated messages in the ChatHistory stream.

    Agent messages are any logging messages with: `AgentLogging.MESSAGE_AUTHOR == AgentLogging.AGENT`. These typically
    are status messages logged in either the `AgentService` or the `Agent` code.
    """

    include_llm_messages: bool = Field(default=True)
    """Whether or not to include LLM-generated messages in the ChatHistory stream.

    LLM messages are any logging messages with: `AgentLogging.MESSAGE_AUTHOR == AgentLogging.LLM`. These typically
    are status messages logged in LLM code (ex: `ChatOpenAI`).
    """

    include_tool_messages: bool = Field(default=True)
    """Whether or not to include Tool-generated messages in the ChatHistory stream.

    LLM messages are any logging messages with: `AgentLogging.MESSAGE_AUTHOR == AgentLogging.TOOL`. These typically
    are status messages logged in Tool code (ex: `GeneratorTool`).
    """

    @property
    def stream_intermediate_events(self):
        return (
            self.include_llm_messages or self.include_agent_messages or self.include_tool_messages
        )
