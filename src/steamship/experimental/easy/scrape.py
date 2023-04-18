"""Quickly adds a file by either downloading it or using a plugin to """
from typing import List, Optional

from pydantic import HttpUrl

from steamship.client.steamship import Steamship
from steamship.data.file import File
from steamship.data.tags.tag import Tag


def scrape(client: Steamship, url: HttpUrl, tags: Optional[List[Tag]] = None):
    return File(client, content="")
