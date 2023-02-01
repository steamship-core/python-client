from typing import Dict, Optional

from steamship import SteamshipError


def interpolate_template(template: str, variables: Optional[Dict] = None) -> str:
    """Interpolate the template with Python formatting semantics. If no variables provided, supply an empty dict."""
    try:
        return template.format(**(variables or {}))
    except KeyError as e:
        raise SteamshipError(
            message="Some variables in the prompt template were not provided.", error=e
        )
