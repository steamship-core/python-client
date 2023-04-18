"""Quickly adds a file by either downloading it or using a plugin to scrape it. Always returns a File object."""
from typing import List, Optional

import requests

from steamship.client.steamship import Steamship
from steamship.data.file import File
from steamship.data.plugin.plugin_instance import PluginInstance
from steamship.data.tags.tag import Tag


def _scrape_with_importer(client: Steamship, url: str, importer: PluginInstance) -> File:
    """Scrape a URL with the provided Importer plugin, and then await the File."""
    task = File.create_with_plugin(client, plugin_instance=importer.handle, url=url)
    task.wait()
    return task.output


def _scrape_with_download(client: Steamship, url: str) -> File:
    """Scrape the bytes of a URL and load it into a File."""
    resp = requests.get(url)
    file = File.create(
        client,
        content=resp.content,
    )
    return file


def _scrape(client: Steamship, url: str) -> File:
    """Do a best effort to scrape the provided URL, returning a File."""
    # Here we do a bit of funny business to pick the right importer.
    if "youtube.com" in url:
        importer = client.use_plugin("youtube-file-importer")
        return _scrape_with_importer(client, url, importer)
    else:
        return _scrape_with_download(client, url)


def scrape(client: Steamship, url: str, tags: Optional[List[Tag]] = None) -> File:
    """Scrape a file via URL, returning a File object no matter what."""
    file = _scrape(client, url)

    # Add the provided tags.
    for tag in tags or []:
        tag.file_id = file.id
        client.post("tag/create", tag, expect=Tag)

    return file
