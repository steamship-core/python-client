"""
Pytest reads this file in before doing any work.

Read more about conftest.py under:
  - https://docs.pytest.org/en/stable/fixture.html
  - https://docs.pytest.org/en/stable/writing_plugins.html
"""

# import pytest

import sys
from pathlib import Path

# Make sure `steamship_tests` is on the PYTHONPATH. Otherwise cross-test imports (e.g. to util libraries) will fail.
sys.path.append(str(Path(__file__).parent.absolute()))
