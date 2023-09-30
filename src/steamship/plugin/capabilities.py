"""Plugin capabilities.

Capabilities are a concept communicated back and forth between plugins and client code via blocks, and they are meant to
indicate client code's need for certain levels of support of a range of features.

Clients can request NATIVE, BEST_EFFORT, or OPTIONAL support for features that a plugin may or may not support.  Plugins
are expected to parse this and fail-fast if the user has requested support for a feature that the plugin does not
support, so that users are not e.g. billed for usage they can't incorporate.

Capability requests can include other information on the request itself, but oftentimes indicate that certain blocks
will be tagged in Steamship-native ways as part of the rest of the payload.  For example, ConversationSupport is a
capability that indicates the CHAT TagKind will be included in blocks that are part of the input, and the plugin is
expected to incorporate these with a model that supports them.

In the case that a Plugin does not support behavior indicated by the Capability request, it will throw, listing the
models that it could not support at the levels requested.  Otherwise, when Plugins respond, they'll include another
block indicating at which level they served the requested capabilities.
"""
import logging
from enum import Enum
from typing import Dict, Iterable, List, Mapping, Optional, Tuple, Type, TypeVar

from pydantic import BaseModel, Extra, Field, validator
from pydantic.dataclasses import ClassVar

from steamship import Block, MimeTypes, SteamshipError
from steamship.agents.schema.functions import OpenAIFunction

CapabilityType = TypeVar("CapabilityType", bound="Capability")


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
    plugin will still report NATIVE.  It is not a requirement that plugins do this, and so many plugins may opt to only
    support their NATIVE levels.
    """

    OPTIONAL = "optional"
    """
    The plugin may ignore this feature when serving content.
    """


class Capability(BaseModel, extra=Extra.allow):
    """Base class for all capabilities."""

    NAME: ClassVar[str]
    """Name of the capability.

    Each capability provides its own name.  When capabilities are deserialized, they become this base Capability class,
    with extra fields appended to them.  This is not included in the init path for a class by default, with the
    intention that classes define their names at a class-definition-level.

    Make an effort to namespace these by organization, since this is technically extensible.
    """

    name: str = Field(init_var=False, default=None)
    """Name of the capability as an instance field.

    The base class of capabilities doesn't have a NAME, but can represent the unresolved Capabilities that clients are
    requesting.  See CapabilityImpl for the setting of this field.
    """

    request_level: RequestLevel = RequestLevel.NATIVE

    def is_plugin_support_valid(
        self, support_level: Optional[RequestLevel]
    ) -> Tuple[bool, Optional["Capability.Response"]]:
        """Checks if the plugin fulfills the capability request level for this specific capability.

        Returns a basic Response if the plugin supports the capability and the support level is at least what the
        consumer asked for.

        :param support_level: The level at which the Plugin asserts that it can support the requested capability
        :return: a bool that indicates whether the Plugin support level is valid, plus an Optional Response for this
          capability's support, if applicable.
        """
        if self.request_level == RequestLevel.OPTIONAL and support_level is None:
            # We don't support it, but it's optional.
            return True, None
        if support_level is None:
            # Not optional, but we don't support it.
            return False, None
        if self.request_level == RequestLevel.NATIVE and support_level != RequestLevel.NATIVE:
            # They want native support, but we don't support it at a native level.
            return False, None
        # They want NATIVE support, and we support that, OR
        # They want BEST_EFFORT support, and we support that, OR
        # They want BEST_EFFORT and we support native
        return True, Capability.Response(fulfilled_at=support_level)

    class Response(BaseModel, extra=Extra.allow):
        """Response regarding a specific capability served by the plugin.

        Responses indicate at minimum the level at which they served the request-level.  They may
        also specify additional metadata.
        """

        CAPABILITY_NAME: ClassVar[str]

        name: str = Field(init_var=False, default=None)
        fulfilled_at: RequestLevel


class CapabilityImpl(Capability, extra=Extra.forbid):
    # TODO (PR): The Extra.forbid here is to enforce clamping of deserialization, but it may just be simpler to leave
    #  that up to individual capabilities?  My goal here is to prevent accidental breakage of contract when someone
    #  provides specific metadata that makes it so e.g. a plugin with an older view of the world thinks it has Best
    #  Effort support but can't because of those extra requests.

    @classmethod
    @validator("name", always=True, pre=True)
    def name_validator(cls, val: str):
        assert val is None or val == cls.NAME
        return cls.NAME

    class ResponseImpl(Capability.Response, extra=Extra.forbid):
        @classmethod
        @validator("name", always=True, pre=True)
        def name_validator(cls, val: str):
            assert val is None or val == cls.CAPABILITY_NAME
            return cls.CAPABILITY_NAME


class UnsupportedCapabilityError(Exception):
    """
    Raised when support for a given feature is requested from a plugin in a non-optional way, but the plugin doesn't
    support it
    """

    def __init__(self, unsupported_capabilities: List[Capability]):
        names = ", ".join([cap.name for cap in unsupported_capabilities])
        super().__init__(
            f"The following features were requested but are not supported by this plugin: {names}"
        )
        self.unsupported_capabilities = unsupported_capabilities


class CapabilityPluginRequest(BaseModel):
    """Model representing the text in a STEAMSHIP_PLUGIN_CAPABILITIES block when it is used as a request."""

    # TODO (PR): Might be cleaner to have separate MIMEs for response/request.
    requested_capabilities: List[Capability]

    @classmethod
    def from_block(cls, block: Block) -> "CapabilityPluginRequest":
        assert block.mime_type == MimeTypes.STEAMSHIP_PLUGIN_CAPABILITIES
        assert block.text
        return cls.parse_raw(block.text)

    def to_block(self) -> Block:
        return Block(text=self.json(), mime_type=MimeTypes.STEAMSHIP_PLUGIN_CAPABILITIES)


class CapabilityPluginResponse(BaseModel):
    """Model representing the text in a STEAMSHIP_PLUGIN_CAPABILITIES block when it is used as a response."""

    capability_responses: List[Capability.Response]

    @classmethod
    def from_block(cls, block: Block) -> "CapabilityPluginResponse":
        assert block.mime_type == MimeTypes.STEAMSHIP_PLUGIN_CAPABILITIES
        assert block.text
        return cls.parse_raw(block.text)

    def to_block(self) -> Block:
        return Block(text=self.json(), mime_type=MimeTypes.STEAMSHIP_PLUGIN_CAPABILITIES)


class RequestedCapabilities:
    _requested: Optional[Dict[str, Capability]]
    _supported_levels: Dict[str, RequestLevel]
    _names_to_types: Dict[str, Type[CapabilityType]]

    def __init__(self, supported_levels: Mapping[Type[CapabilityType], RequestLevel]):
        self._requested = None
        self._supported_levels = {
            cap_type.NAME: request_level for cap_type, request_level in supported_levels.items()
        }
        self._names_to_types = {cap_type.NAME: cap_type for cap_type in supported_levels.keys()}

    def __contains__(self, typ: Type[CapabilityType]):
        return self.get(typ) is not None

    def __getitem__(self, typ: Type[CapabilityType]):
        v = self.get(typ)
        if v is None:
            raise KeyError(typ)
        return v

    def load_requests(self, request: CapabilityPluginRequest) -> CapabilityPluginResponse:
        """
        Load requests from a CapabilityPluginRequest into this mapping and verify that we can support the requested
        capabilities.

        :param request: The CapabilityPluginRequest provided to the Plugin
        :return: a CapabilityPluginResponse which indicates the level at which we are serving each request
        """
        unsupported = []
        responses = []
        self._requested = {}
        for requested_capability in request.requested_capabilities:
            support_level = self._supported_levels.get(requested_capability.name)
            is_valid, response = requested_capability.is_plugin_support_valid(support_level)
            if not is_valid:
                unsupported.append(requested_capability)
            if response:
                responses.append(response)
            self._requested[requested_capability.name] = requested_capability

        if unsupported:
            raise UnsupportedCapabilityError(unsupported)
        return CapabilityPluginResponse(capability_responses=responses)

    def extract_from_blocks(self, blocks: Iterable[Block]) -> CapabilityPluginResponse:
        """Find the block in a list that defines capability requests, and initialize this data structure with it.

        It may be the case that there is no block indicating capability requests; Older clients may be passing blocks
        to the plugin without programmatic knowledge of capabilities.

        :param blocks: A list of blocks that was passed as input to a plugin
        :return: a CapabilityPluginResponse which indicates the level at which we are serving each request
        """
        capabilities_block = None
        for block in blocks:
            if block.mime_type == MimeTypes.STEAMSHIP_PLUGIN_CAPABILITIES:
                if capabilities_block is not None:
                    logging.error(
                        f"Found more than one block with MIME_TYPE {MimeTypes.STEAMSHIP_PLUGIN_CAPABILITIES} in request blocks.  Using first one found."
                    )
                    break
                capabilities_block = block
        if not capabilities_block:
            return CapabilityPluginResponse(capability_responses=[])
        return self.load_requests(CapabilityPluginRequest.parse_raw(capabilities_block.text))

    def get(
        self, typ: Type[CapabilityType], default: Optional[CapabilityType] = None
    ) -> Optional[CapabilityType]:
        if self._requested is None:
            raise SteamshipError(
                "RequestedCapabilities has not been loaded with a set of requests yet.  Load a request with .load_requests()"
            )
        capability = self._requested.get(typ.NAME)
        if capability:
            return typ.parse_obj(capability)
        return default


class SystemPromptSupport(CapabilityImpl):
    """This plugin supports system prompts separate from the per-request model prompt.

    The system prompt will come across in other blocks on the request.
    """

    name = "steamship.system_prompt_support"

    request_level = RequestLevel.BEST_EFFORT
    """
    If NATIVE, asserts that the model being used supports System Prompt in a first-class capacity.
    If BEST_EFFORT, the system prompt will be incorporated into the request in another way, usually via concatenation
      with the prompt.
    """


class ConversationSupport(CapabilityImpl):
    """This plugin supports conversations.

    The content of the conversation will come across in other blocks on the request, using the CHAT TagKind.
    """

    name = "steamship.conversation_support"


class FunctionCallingSupport(CapabilityImpl):
    """This plugin supports function calling.

    Function definitions come across as a list of function definitions.
    """

    name = "steamship.function_calling_support"

    functions: List[OpenAIFunction]
    # TODO (PR): Worth generalizing this?
