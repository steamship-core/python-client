from typing import Dict, Any, Optional

def safe_get(dict: Dict, key: str, default: Any=None) -> Optional[Any]:
    """Safely a value from dictionairy using a specific key"""
    return dict.get(key, default) or default