from typing import Any, Optional

from steamship import File


def first_value(file: File, tag_kind: str, value_key: str) -> Optional[Any]:
    """Return the value of the first block tag found in a file for the kind and value_key specified."""
    for block in file.blocks:
        for block_tag in block.tags:
            if block_tag.kind == tag_kind:
                return block_tag.value.get(value_key, "")
    return None
