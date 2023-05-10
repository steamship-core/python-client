"""Common utilities for the Steamship Python API"""
import os
import sys
import traceback
from importlib import machinery
from pathlib import Path

import click

from steamship.base.error import SteamshipError


def find_api_py() -> Path:
    path = Path("src/api.py")
    if not path.exists():
        path = Path("api.py")
        if not path.exists():
            raise SteamshipError("Could not find api.py either in root directory or in src.")
    return path


def get_api_module(path: Path):
    try:
        sys.path.append(str(path.parent.absolute()))

        # load the API module to allow config inspection / generation
        return machinery.SourceFileLoader("api", str(path)).load_module()
    except Exception:
        click.secho(
            "An error occurred while loading your api.py to check configuration parameters. Full stack trace below.",
            fg="red",
        )
        traceback.print_exc()
        click.get_current_context().abort()
        return None


def is_in_replit() -> bool:
    """Returns True if the user appears to be inside Replit."""
    if os.environ.get("REPLIT_CLI") or os.environ.get("REPLIT_DB_URL"):
        return True

    return False
