from typing import List, Optional

from steamship.data.tags.tag import Tag


def get_tag(
    tags: Optional[List[Tag]], kind: Optional[str] = None, name: Optional[str] = None
) -> Optional[Tag]:
    """Return the first tag of a list with the provided kind & name."""
    for tag in tags or []:
        if (kind is None or tag.kind == kind) and (name is None or tag.name == name):
            return tag
    return None


def get_tag_value_key(
    tags: Optional[List[Tag]], key: str, kind: Optional[str] = None, name: Optional[str] = None
) -> Optional[any]:
    """Return the value key from the first tag of a list with the provided kind & name."""
    if tag := get_tag(tags, kind=kind, name=name):
        return (tag.value or {}).get(key)
    return None
