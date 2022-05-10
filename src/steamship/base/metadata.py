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
