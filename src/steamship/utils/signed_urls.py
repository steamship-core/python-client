import logging
import os
import uuid
import tempfile
import urllib
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, parse_qs

import requests

from steamship import SteamshipError


def download_from_signed_url(url: str, to_file: Path = None) -> Path:
    """
    Downloads the Signed URL to the filename `desired_filename` in a temporary directory on disk.
    """
    logging.info(f"Downloading: {url} to {to_file} in a temporary directory")

    # Ensure the path to the desired file exists
    if not os.path.exists(to_file.parent):
        os.makedirs(to_file.parent)

    with open(to_file, 'wb') as f:
        resp = requests.get(url)
        logging.info(f"Got contents of: {url}")
        content = resp.content
        f.write(content)
        logging.info(f"Wrote contents of: {url} to {to_file}")
    return Path(to_file)


def upload_to_signed_url(url: str, bytes: Optional[bytes] = None, filepath: Optional[Path] = None):
    """
    Uploads either the bytes or filepath contents to the provided Signed URL.
    """
    if bytes is not None:
        logging.info(f"Uploading provided bytes to: {url}")
    elif filepath is not None:
        logging.info(f"Uploading file at {filepath} to: {url}")
        with open(filepath, 'rb') as f:
            bytes = f.read()
    else:
        raise SteamshipError(
            message="Unable to upload data to signed URL -- neither a filepath nor bytes were provided.",
            suggestion="Please provide either the `bytes` or the `filepath` argument"
        )

    files = {'file': (filepath, bytes)}
    parsed_url = urllib.parse.urlparse(url)

    if "amazonaws.com" in parsed_url.netloc:
        # When uploading to AWS Production, the format of the URL should be https://BUCKET.DOMAIN/KEY
        http_response = requests.put(url, data={}, files=files)
    else:
        # When uploading to AWS Localstack, the format of the URL should be https://DOMAIN/BUCKET
        # And we must, in addition, re-format the POST request. This appears to be a quick of using Localstack
        # and here should be considered a special case to enable testing.
        logging.info("Space.upload_to_signed_url is using the LOCALSTACK upload strategy.")

        params = parse_qs(parsed_url.query)
        params = {p: params[p][0] for p in params}
        path_parts = parsed_url.path.lstrip("/").split("/")
        bucket = path_parts[0]

        # This result in http://DOMAIN/BUCKET
        newurl = f"{parsed_url.scheme}://{parsed_url.netloc}/{bucket}"

        # The key, and a selected subset of the former query args, become multi-part mime data
        key = "/".join(path_parts[1:])
        data = {
            'key': key,
            'AWSAccessKeyId': params['X-Amz-Credential'].split('/')[0],
            'signature': params['X-Amz-Signature']
        }
        http_response = requests.post(newurl, data=data, files=files)

    # S3 returns 204 upon success; we include 200 here for safety.
    if http_response.status_code not in [200, 204]:
        logging.error(f"File upload error. file={filepath}. url= {url}")
        logging.error(f"Status Code: {http_response.status_code}")
        logging.error(f"Response Text: {http_response.text}")
        raise SteamshipError(
            message=f"Unable to upload data to signed URL. Status code: {http_response.status_code}. Status text: {http_response.text}"
        )
