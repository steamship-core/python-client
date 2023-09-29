import pytest

from steamship.plugin.capabilities import CapabilityImpl, RequestLevel


@pytest.mark.parametrize(
    ("request_level", "support_level", "expected_support_valid", "expected_none_response"),
    [
        (RequestLevel.NATIVE, RequestLevel.NATIVE, True, False),
        (RequestLevel.NATIVE, RequestLevel.BEST_EFFORT, False, True),
        (RequestLevel.NATIVE, None, False, True),
        (RequestLevel.BEST_EFFORT, RequestLevel.NATIVE, True, False),
        (RequestLevel.BEST_EFFORT, RequestLevel.BEST_EFFORT, True, False),
        (RequestLevel.BEST_EFFORT, None, False, True),
        (RequestLevel.OPTIONAL, RequestLevel.NATIVE, True, False),
        (RequestLevel.OPTIONAL, RequestLevel.BEST_EFFORT, True, False),
        (RequestLevel.OPTIONAL, None, True, True),
    ],
)
def test_is_plugin_support_valid(
    request_level, support_level, expected_support_valid, expected_none_response
):
    class TestCapability(CapabilityImpl):
        name = "steamship.test_capability"

    request = TestCapability(request_level=request_level)
    is_valid, response = request.is_plugin_support_valid(support_level)
    assert is_valid == expected_support_valid
    if expected_none_response:
        assert response is None
    else:
        assert response is not None
        assert response.fulfilled_at == support_level
