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
    localstack_hostname = environ.get("LOCALSTACK_HOSTNAME")
    if url and localstack_hostname is not None and localstack_hostname != "localhost":
        for host in ["127.0.0.1", "host.docker.internal", "localstack"]:
            url = url.replace(host, localstack_hostname)
            logging.info(f"Replacing domain {host} in {url} with {localstack_hostname}")
    return url
