from typing import Any, Dict, Optional


def safe_get(d: Dict, key: str, default: Any = None) -> Optional[Any]:
    """Safely a value from dictionairy using a specific key"""
    return d.get(key, default) or default
