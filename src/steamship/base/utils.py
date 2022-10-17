from typing import Optional


def format_uri(uri: Optional[str]) -> Optional[str]:
    if uri is not None and not uri.endswith("/"):
        uri += "/"
    return uri
