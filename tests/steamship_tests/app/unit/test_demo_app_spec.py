import pprint
from typing import Callable, Optional

import pytest
from assets.packages.demo_package import TestPackage


@pytest.mark.parametrize("invocable_handler", [TestPackage], indirect=True)
def test_app_spec(invocable_handler: Callable[[str, str, Optional[dict]], dict]):
    """Test that the handler returns the proper directory information"""
    response_dict = invocable_handler("GET", "/__dir__", {})
    pp = pprint.PrettyPrinter(indent=4)
    print()
    pp.pprint(response_dict)
