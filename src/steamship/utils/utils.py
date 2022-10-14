from typing import Any, Dict, Optional


def safe_get(d: Dict, key: str, default: Any = None) -> Optional[Any]:
    """Safely a value from dictionairy using a specific key"""
    return d.get(key, default) or default


def format_uri(uri: Optional[str]) -> Optional[str]:
    if uri is not None and not uri.endswith("/"):
        uri += "/"
    return uri
