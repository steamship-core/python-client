from typing import Any, Dict

from steamship import Steamship
from steamship.invocable import Invocable


class BadPackage(Invocable):
    """Bad Package should not start when deployed."""

    def __init__(self, client: Steamship = None, config: Dict[str, Any] = None):
        super().__init__(client, config)
        raise RuntimeError("this should fail immediately")
