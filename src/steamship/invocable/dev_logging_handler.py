from logging import StreamHandler
from typing import List, Tuple, cast

from fluent.handler import FluentRecordFormatter

LOGGING_FORMAT = {
    "level": "%(levelname)s",
    "host": "%(hostname)s",
    "where": "%(module)s.%(filename)s.%(funcName)s:%(lineno)s",
    "type": "%(levelname)s",
    "stack_trace": "%(exc_text)s",
    "message_type": "%(message_type)s",
    "component_name": "%(component_name)s",
}


class LoggingKeys:
    MESSAGE_TYPE = "message_type"
    COMPONENT_NAME = "component_name"


class MessageTypes:
    USER_INPUT = "user-input"
    USER_OUTPUT = "user-output"
    TOOL_OUTPUT = "tool-output"
    TOOL_INPUT = "tool-input"
    AGENT_OUTPUT = "agent-output"
    AGENT_INPUT = "agent-output"


class DevelopmentLoggingHandler(StreamHandler):
    """A logging handler for developing Steamship Agents, Tools, Packages, and Plugins locally."""

    tab_index: int
    context_stack: List[Tuple[str, str]]

    def __init__(self):
        StreamHandler.__init__(self)
        formatter = FluentRecordFormatter(LOGGING_FORMAT, fill_missing_fmt_key=True)
        self.setFormatter(formatter)
        self.tab_index = 0
        self.reset_stack()

    def spacer(self):
        tabs = len(self.context_stack)
        if tabs == 0:
            return ""
        return f"{'..' * tabs} || "

    def push(self, type: str, name: str, message_dict: dict):
        self.context_stack.append((type, name))
        level = message_dict.get("level", None)
        message = message_dict.get("message", None)
        print(f"{self.spacer()}Entering {type}/{name}")
        print(f"{self.spacer()}{level} {message}")

    def reset_stack(self):
        self.context_stack = []

    def pop(self):
        self.context_stack.pop()

    def emit_with_stack(self, message_dict: dict):
        level = message_dict.get("level", None)
        message = message_dict.get("message", None)
        print(f"{self.spacer()}{level} {message}")

    def emit(self, record):
        message_dict = cast(dict, self.format(record))

        component_name = message_dict.get(LoggingKeys.COMPONENT_NAME, None)
        message_type = message_dict.get(LoggingKeys.MESSAGE_TYPE, None)

        if message_type == MessageTypes.USER_INPUT:
            self.reset_stack()
            self.push("User", "", message_dict)
        elif message_type == MessageTypes.AGENT_INPUT:
            self.reset_stack()
            self.push("Agent", component_name, message_dict)
        elif message_type == MessageTypes.TOOL_INPUT:
            self.reset_stack()
            self.push("Tool", component_name, message_dict)
        else:
            self.emit_with_stack(message_dict)

        if message_type in [MessageTypes.TOOL_INPUT, MessageTypes.TOOL_OUTPUT]:
            self.emit_with_stack(message_dict)
