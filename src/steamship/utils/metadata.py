import hashlib
import json
from typing import Dict, List, Optional, Union

Metadata = Union[int, float, bool, str, List, Dict]


def str_to_metadata(s: str) -> Optional[Metadata]:
    if s is None:
        return None
    return json.loads(s)


def metadata_to_str(m: Metadata) -> Optional[str]:
    if m is None:
        return None
    return json.dumps(m)


def hash_dict(d: Dict) -> str:
    """Returns the MD5 hash of a dictionary."""
    dhash = hashlib.md5()  # noqa: S303, S324
    encoded = json.dumps(d, sort_keys=True).encode()
    dhash.update(encoded)
    return dhash.hexdigest()
