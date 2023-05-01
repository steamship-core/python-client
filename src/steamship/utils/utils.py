from typing import Any, Dict, Optional

from steamship.utils.metadata import hash_dict


def safe_get(d: Dict, key: str, default: Any = None) -> Optional[Any]:
    """Safely a value from dictionairy using a specific key"""
    return d.get(key, default) or default


def format_uri(uri: Optional[str]) -> Optional[str]:
    if uri is not None and not uri.endswith("/"):
        uri += "/"
    return uri


def create_instance_handle(
    invocable_handle: str, version_handle: str, invocable_config: Optional[Dict[str, Any]]
) -> str:
    """Create an instance handle deterministically from package/plugin metadata and configuration."""
    return f"{invocable_handle}-{hash_dict({**invocable_config, 'version': version_handle})}"
