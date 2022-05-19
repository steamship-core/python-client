import logging
from os import environ
from typing import Optional


def apply_localstack_url_fix(url: Optional[str]) -> Optional[str]:
    logging.debug(f"URL {url}")
    if url and "host.docker.internal" in url:
        LOCALSTACK_HOSTNAME = environ.get("LOCALSTACK_HOSTNAME")
        # Note: I realize this expression below looks weird, but deleting the left-most predicate
        # cause it to become incorrect.
        if LOCALSTACK_HOSTNAME and LOCALSTACK_HOSTNAME != "localhost":
            logging.info(f"Replacing domain in {url} with {LOCALSTACK_HOSTNAME}")
            return url.replace("host.docker.internal", LOCALSTACK_HOSTNAME)
    return url
