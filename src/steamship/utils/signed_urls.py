import json
import logging
from pathlib import Path
from typing import Optional

import requests

from steamship import SteamshipError
from steamship.utils.url import apply_localstack_url_fix


def url_to_json(url: str) -> any:
    """
    Downloads the Signed URL and returns the contents as JSON.
    """
    bytes = url_to_bytes(url)
    json_string = bytes.decode("utf8")
    return json.loads(json_string)


def url_to_bytes(url: str) -> bytes:
    """
    Downloads the Signed URL and returns the contents as bytes.

    This is a helper function to consolidate Steamship Client URL fetching to ensure a single point of handling for:
      * Error messages
      * Any required manipulations for URL signed URLs
      * Any required manipulations for localstack-based environments

    Note that the base API Client does not use this method on purpose: in the event of error code, it inspects the
    contents of the response for a SteamshipError.
    """
    url = apply_localstack_url_fix(url)
    logging.info(f"Downloading: {url}.")

    resp = requests.get(url)
    if resp.status_code != 200:
        # TODO: At least Localstack send to reply with HTTP 200 even if the file isn't found!
        # The full response contains:
        # <Error>
        #     <Code>NoSuchKey</Code>
        #
        # So we **could** check the response text even in the event of 200 but that seems wrong..
        if "<Code>NoSuchKey</Code>" in resp.text:
            raise SteamshipError(
                message=f"The file at signed URL {url} did not exist. HTTP {resp.status_code}. Content: {resp.text}"
            )
        else:
            raise SteamshipError(
                message=f"There was an error downloading from the signed url: {url}. HTTP {resp.status_code}. Content: {resp.text}"
            )
    return resp.content


def download_from_signed_url(url: str, to_file: Path = None) -> Path:
    """
    Downloads the Signed URL to the filename `desired_filename` in a temporary directory on disk.
    """
    content = url_to_bytes(url)

    if not to_file.parent.exists():
        to_file.parent.mkdir(parents=True, exist_ok=True)

    with open(to_file, "wb") as f:
        logging.debug(f"Got contents of: {url}")
        f.write(content)
        logging.debug(f"Wrote contents of: {url} to {to_file}")
    return Path(to_file)


def upload_to_signed_url(url: str, _bytes: Optional[bytes] = None, filepath: Optional[Path] = None):
    """
    Uploads either the bytes or filepath contents to the provided Signed URL.
    """

    url = apply_localstack_url_fix(url)
    if _bytes is not None:
        logging.info(f"Uploading provided bytes to: {url}")
    elif filepath is not None:
        logging.info(f"Uploading file at {filepath} to: {url}")
        with open(filepath, "rb") as f:
            _bytes = f.read()
    else:
        raise SteamshipError(
            message="Unable to upload data to signed URL -- neither a filepath nor bytes were provided.",
            suggestion="Please provide either the `bytes` or the `filepath` argument",
        )

    http_response = requests.put(
        url, data=_bytes, headers={"Content-Type": "application/octet-stream"}
    )

    # S3 returns 204 upon success; we include 200 here for safety.
    if http_response.status_code not in [200, 204]:
        logging.error(f"File upload error. file={filepath}. url= {url}")
        logging.error(f"Status Code: {http_response.status_code}")
        logging.error(f"Response Text: {http_response.text}")
        raise SteamshipError(
            message=f"Unable to upload data to signed URL. Status code: {http_response.status_code}. Status text: {http_response.text}"
        )
