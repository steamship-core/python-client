import pytest
from assets.packages.demo_package import TestPackage

ERROR_NO_METHOD = "No handler for POST /method_doesnt_exist available."
ERROR_STEAMSHIP_ERROR = "[ERROR - POST raise_steamship_error] raise_steamship_error"
ERROR_PYTHON_ERROR = "[ERROR - POST raise_python_error] raise_python_error"


@pytest.mark.parametrize("invocable_handler", [TestPackage], indirect=True)
def test_instance_invoke_unit(invocable_handler):
    """Test that the handler returns the proper errors"""

    response = invocable_handler("POST", "method_doesnt_exist")
    assert response.get("status", {}).get("statusMessage", "") == ERROR_NO_METHOD

    response = invocable_handler("POST", "raise_steamship_error")
    assert response.get("status", {}).get("statusMessage", "") == ERROR_STEAMSHIP_ERROR

    response = invocable_handler("POST", "raise_python_error")
    assert response.get("status", {}).get("statusMessage", "") == ERROR_PYTHON_ERROR
