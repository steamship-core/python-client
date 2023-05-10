from typing import List, Optional

from steamship import Tag


def get_tag_value_key(
    tags: Optional[List[Tag]], key: str, kind: Optional[str] = None, name: Optional[str] = None
) -> Optional[any]:
    """Iterates through a list of tags and returns the first that contains the provided Kind/Name/ValueKey."""
    for tag in tags or []:
        if (kind is None or tag.kind == kind) and (name is None or tag.name == name):
            return (tag.value or {}).get(key)
    return None
