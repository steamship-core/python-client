from typing import Callable, Optional

import pytest
from assets.apps.demo_app import TestApp

ERROR_NO_METHOD = "No handler for POST /method_doesnt_exist available."
ERROR_STEAMSHIP_ERROR = "[ERROR - POST raise_steamship_error] raise_steamship_error"
ERROR_PYTHON_ERROR = "[ERROR - POST raise_python_error] raise_python_error"


@pytest.mark.parametrize("app_handler", [TestApp], indirect=True)
def test_instance_invoke_unit(app_handler: Callable[[str, str, Optional[dict]], dict]):
    """Test that the handler returns the proper errors"""

    response = app_handler("POST", "method_doesnt_exist")
    assert response.get("status", {}).get("statusMessage", "") == ERROR_NO_METHOD

    response = app_handler("POST", "raise_steamship_error")
    assert response.get("status", {}).get("statusMessage", "") == ERROR_STEAMSHIP_ERROR

    response = app_handler("POST", "raise_python_error")
    assert response.get("status", {}).get("statusMessage", "") == ERROR_PYTHON_ERROR
