import json
from typing import Union, List, Dict

Metadata = Union[int, float, bool, str, List, Dict]


def str_to_metadata(s: str) -> Metadata:
    if s is None:
        return None
    try:
        return json.loads(s)
    except:
        s


def metadata_to_str(m: Metadata) -> str:
    if m is None:
        return None
    try:
        return json.dumps(m)
    except:
        m
