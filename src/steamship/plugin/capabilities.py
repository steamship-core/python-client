from abc import ABC
from enum import Enum
from typing import Iterable, List, Optional

from pydantic import BaseModel, Field

from steamship import Block, MimeTypes
from steamship.agents.schema.functions import OpenAIFunction


class RequestLevel(Enum):
    """Specifies how the Plugin should handle the request for support of a specific feature."""

    NATIVE = "native"
    """
    The plugin user is requesting that the plugin supports this feature as a first-class feature.
    """

    BEST_EFFORT = "best-effort"
    """
    The plugin may choose to make a best effort to support the requested feature.  For example, the plugin may craft
    a prompt to a model in a way that attempts to support the feature and parse the output appropriately.

    If the plugin supports the feature at a native level, but the request_level from the user was BEST_EFFORT, the
    plugin will still report NATIVE.
    """

    OPTIONAL = "optional"
    """
    The plugin may ignore this feature when serving content.
    """


class Capability(ABC, BaseModel):
    """Base class for all capabilities."""

    name: str = Field(init_var=False)
    request_level: RequestLevel = RequestLevel.NATIVE

    class Response(BaseModel):
        """Response regarding a specific capability served by the plugin.

        Responses indicate at minimum the level at which they served the request-level.  They may
        also specify additional metadata.
        """

        fulfilled_at: RequestLevel


class UnsupportedCapabilityError(Exception):
    """
    Raised when support for a given feature is requested from a plugin in a non-optional way, but the plugin doesn't
    support it
    """

    def __init__(self, unsupported_capabilities: List[Capability]):
        super().__init__(
            f"The following features were requested but are not supported by this plugin: {unsupported_capabilities}"
        )
        self.unsupported_capabilities = unsupported_capabilities


class CapabilityPluginRequest(BaseModel):
    requested_capabilities: List[Capability]

    @classmethod
    def from_block(cls, block: Block) -> "CapabilityPluginRequest":
        assert block.mime_type == MimeTypes.STEAMSHIP_PLUGIN_CAPABILITIES
        assert block.text
        return cls.parse_raw(block.text)


class CapabilityPluginResponse(BaseModel):
    capability_responses: List[Capability.Response]

    @classmethod
    def from_block(cls, block: Block) -> "CapabilityPluginResponse":
        assert block.mime_type == MimeTypes.STEAMSHIP_PLUGIN_CAPABILITIES
        assert block.text
        return cls.parse_raw(block.text)


def assert_capabilities(
    request: CapabilityPluginRequest,
    native: Optional[Iterable[Capability]] = None,
    best_effort: Optional[Iterable[Capability]] = None,
) -> CapabilityPluginResponse:
    ...


class SystemPromptSupport(Capability):
    """This plugin supports system prompts separate from the per-request model prompt.

    The system prompt will come across in other blocks on the request.
    """

    request_level = RequestLevel.BEST_EFFORT
    """
    If NATIVE, asserts that the model being used supports System Prompt in a first-class capacity.
    If BEST_EFFORT, the system prompt will be incorporated into the request in another way, usually via concatenation
      with the prompt.
    """


class ConversationSupport(Capability):
    """This plugin supports conversations.

    The content of the conversation will come across in other blocks on the request, using the CHAT TagKind.
    """


class FunctionSupport(Capability):
    """This plugin supports function calling.

    Function definitions come across as a list of function definitions.
    """

    functions: List[OpenAIFunction]
