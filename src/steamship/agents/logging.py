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
    IS_MESSAGE = "is_message"

    MESSAGE_TYPE = "agent_message_type"
    THOUGHT = "thought"
    OBSERVATION = "observation"
    ACTION = "action"
    MESSAGE = "message"

    MESSAGE_AUTHOR = "message_author"
    USER = "user"
    AGENT = "agent"
    TOOL = "tool"
    SYSTEM = "system"
