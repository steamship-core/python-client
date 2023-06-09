import logging
from logging import StreamHandler
from typing import cast

from fluent.handler import FluentRecordFormatter

from steamship.agents.logging import AgentLogging

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


class DevelopmentLoggingHandler(StreamHandler):
    """A logging handler for developing Steamship Agents, Tools, Packages, and Plugins locally."""

    log_level: any
    log_level_with_message_type: any

    def __init__(self, log_level: any = logging.WARN, log_level_for_messages: any = logging.INFO):
        StreamHandler.__init__(self)
        formatter = FluentRecordFormatter(LOGGING_FORMAT, fill_missing_fmt_key=True)
        self.setFormatter(formatter)
        self.log_level = log_level
        self.log_level_for_messages = log_level_for_messages

    def _emit_regular(self, message_dict: dict):
        level = message_dict.get("level", None)
        message = message_dict.get("message", None)
        print(f"[{level}] {message}")

    def _emit_message(self, message_dict: dict):
        author = message_dict.get(AgentLogging.MESSAGE_AUTHOR, "Unknown")
        message = message_dict.get("message", None)
        message_type = message_dict.get(AgentLogging.MESSAGE_TYPE, AgentLogging.MESSAGE)

        print(f"[{author} {message_type}] {message}")

    def emit(self, record):
        """Emit the record, printing it to console out.

        We rely on TWO logging levels for the mechanics of this LoggingHandler:

        - One for standard logging
        - One for specific system Agent-related events, flagged with metadata

        This is to permit INFO-level logging of key Agent/Tool actions without committing the user to see all
        INFO-level logging globally.

        A future implementation may use a cascade of loggers attached to the AgentContext to do this more cleanly.
        """
        message_dict = cast(dict, self.format(record))

        # It will be returned as a string representation of a bool
        is_message = message_dict.get(AgentLogging.IS_MESSAGE, None) == "True"

        if record.levelno >= self.log_level and not is_message:
            return self._emit_regular(message_dict)
        elif record.levelno >= self.log_level_for_messages and is_message:
            return self._emit_message(message_dict)
