import re
from typing import Optional

import inflection


def format_uri(uri: Optional[str]) -> Optional[str]:
    if uri is not None and not uri.endswith("/"):
        uri += "/"
    return uri


def to_snake_case(s: str) -> str:
    return inflection.underscore(s)


def to_camel(s: str) -> str:
    s = re.sub("_(url)$", lambda m: f"_{m.group(1).upper()}", s)
    return inflection.camelize(s, uppercase_first_letter=False)
