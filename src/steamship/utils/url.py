import logging
from enum import Enum
from os import environ
from typing import Optional


class Verb(str, Enum):
    GET = "GET"
    POST = "POST"


def is_local(base: str) -> bool:
    """Check if we are running the client locally."""
    return any(
        local_base in base
        for local_base in ("localhost", "127.0.0.1", "0:0:0:0", "host.docker.internal", "/test:")
    )


def apply_localstack_url_fix(url: Optional[str]) -> Optional[str]:
    logging.debug(f"URL {url}")
    if url and "host.docker.internal" in url:
        localstack_hostname = environ.get("LOCALSTACK_HOSTNAME")
        # Note: I realize this expression below looks weird, but deleting the left-most predicate
        # cause it to become incorrect.
        if localstack_hostname and localstack_hostname != "localhost":
            logging.info(f"Replacing domain in {url} with {localstack_hostname}")
            return url.replace("host.docker.internal", localstack_hostname)
    return url
