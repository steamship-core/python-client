from typing import List

import pytest

from steamship import Block, Tag
from steamship.data import TagKind
from steamship.data.tags.tag_constants import ChatTag
from steamship.plugin.capabilities import (
    Capability,
    CapabilityImpl,
    CapabilityPluginRequest,
    CapabilityPluginResponse,
    ConversationSupport,
    FunctionCallingSupport,
    RequestedCapabilities,
    RequestLevel,
    SupportLevel,
    SystemPromptSupport,
    UnsupportedCapabilityError,
)


class TestCapability(CapabilityImpl):
    NAME = "steamship.test_capability"


class AnotherTestCapability(CapabilityImpl):
    NAME = "steamship.test_capability_2"


@pytest.mark.parametrize(
    ("request_level", "support_level", "expected_support_valid", "expected_none_response"),
    [
        (RequestLevel.NATIVE, SupportLevel.NATIVE, True, False),
        (RequestLevel.NATIVE, SupportLevel.BEST_EFFORT, False, True),
        (RequestLevel.NATIVE, None, False, True),
        (RequestLevel.BEST_EFFORT, SupportLevel.NATIVE, True, False),
        (RequestLevel.BEST_EFFORT, SupportLevel.BEST_EFFORT, True, False),
        (RequestLevel.BEST_EFFORT, None, False, True),
        (RequestLevel.OPTIONAL, SupportLevel.NATIVE, True, False),
        (RequestLevel.OPTIONAL, SupportLevel.BEST_EFFORT, True, False),
        (RequestLevel.OPTIONAL, None, True, True),
        (RequestLevel.DISABLE, SupportLevel.NATIVE | SupportLevel.CAN_DISABLE, True, False),
        (RequestLevel.DISABLE, SupportLevel.BEST_EFFORT | SupportLevel.CAN_DISABLE, True, False),
        (RequestLevel.DISABLE, SupportLevel.NATIVE, False, True),
        (RequestLevel.DISABLE, SupportLevel.BEST_EFFORT, False, True),
        (RequestLevel.DISABLE, None, True, True),
    ],
)
def test_is_plugin_support_valid(
    request_level, support_level, expected_support_valid, expected_none_response
):
    request = TestCapability(request_level=request_level)
    is_valid, response = request.is_plugin_support_valid(support_level)
    assert is_valid == expected_support_valid
    if expected_none_response:
        assert response is None
    else:
        assert response is not None
        assert response.fulfilled_at in support_level


def test_builtin_capabilities_support():
    original_capabilities = {
        ConversationSupport: ConversationSupport(),
        SystemPromptSupport: SystemPromptSupport(),
        FunctionCallingSupport: FunctionCallingSupport(functions=[]),
    }
    original = CapabilityPluginRequest(requested_capabilities=list(original_capabilities.values()))
    block = original.to_block()
    roundtripped = CapabilityPluginRequest.from_block(block)
    assert original == roundtripped
    requested_capabilities = RequestedCapabilities(
        {cap_typ: SupportLevel.NATIVE for cap_typ in original_capabilities.keys()}
    )
    requested_capabilities.load_requests(roundtripped)
    for cap_typ in original_capabilities.keys():
        requested = requested_capabilities.get(cap_typ)
        assert requested == original_capabilities[cap_typ]


def test_capability_plugin_request_block_roundtrips():
    original = CapabilityPluginRequest(
        requested_capabilities=[TestCapability(request_level=RequestLevel.NATIVE)]
    )
    block = original.to_block()
    roundtripped = CapabilityPluginRequest.from_block(block)
    assert original == roundtripped


def test_capability_plugin_response_block_roundtrips():
    original = CapabilityPluginResponse(
        capability_responses=[Capability.Response(fulfilled_at=SupportLevel.NATIVE)]
    )
    block = original.to_block()
    roundtripped = CapabilityPluginResponse.from_block(block)
    assert original == roundtripped


def _make_input_blocks() -> List[Block]:
    return [
        Block(
            text="Can you make me an image of a whale?",
            tags=[Tag(kind=TagKind.CHAT, name=ChatTag.HISTORY)],
        ),
        Block(text="Sure!  Here's an image:", tags=[Tag(kind=TagKind.CHAT, name=ChatTag.ROLE)]),
    ]


def test_requested_capabilities_extract():
    request = CapabilityPluginRequest(
        requested_capabilities=[
            TestCapability(request_level=RequestLevel.NATIVE),
            AnotherTestCapability(request_level=RequestLevel.OPTIONAL),
        ]
    )
    blocks = _make_input_blocks()
    blocks.append(request.to_block())

    req_caps = RequestedCapabilities(supported_levels={TestCapability: SupportLevel.NATIVE})
    response = req_caps.extract_from_blocks(blocks)
    assert response == CapabilityPluginResponse(
        capability_responses=[TestCapability.Response(fulfilled_at=SupportLevel.NATIVE)]
    )

    test_capability = req_caps[TestCapability]
    assert test_capability == TestCapability(request_level=RequestLevel.NATIVE)


def test_no_requested_capabilities():
    req_caps = RequestedCapabilities(supported_levels={TestCapability: SupportLevel.NATIVE})
    response = req_caps.extract_from_blocks(_make_input_blocks())
    assert response is None


def test_unsupported_requested_capabilities():
    request = CapabilityPluginRequest(
        requested_capabilities=[TestCapability(request_level=RequestLevel.NATIVE)]
    )
    req_caps = RequestedCapabilities(supported_levels={})
    with pytest.raises(UnsupportedCapabilityError):
        req_caps.extract_from_blocks([request.to_block()])
