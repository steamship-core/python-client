"""Collection of unit steamship_tests and integration steamship_tests for the steamship client."""
from pathlib import Path

ROOT_PATH = Path(__file__).parent.parent.parent
VENV_PATH = ROOT_PATH / ".venv"
SRC_PATH = ROOT_PATH / "src"
TEST_PATH = Path(__file__).parent.parent
TEST_ASSETS_PATH = TEST_PATH / "assets"
PACKAGES_PATH = TEST_ASSETS_PATH / "packages"
PLUGINS_PATH = TEST_ASSETS_PATH / "plugins"
