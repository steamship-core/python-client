from typing import Callable, Optional

import pytest
from assets.apps.demo_app import TestApp


@pytest.mark.parametrize("app_handler", [TestApp], indirect=True)
def test_app_spec(app_handler: Callable[[str, str, Optional[dict]], dict]):
    """Test that the handler returns the proper directory information"""
    response_dict = app_handler("POST", "/hello", {})
    print(response_dict)
