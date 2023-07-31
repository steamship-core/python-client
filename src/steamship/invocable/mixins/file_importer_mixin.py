import logging
import os
from typing import List, Optional, Tuple
from urllib.parse import urlparse

import requests

from steamship import DocTag, File, MimeTypes, Steamship, SteamshipError, Tag, Task
from steamship.data import TagKind
from steamship.data.tags.tag_constants import StatusTagName
from steamship.invocable import post
from steamship.invocable.package_mixin import PackageMixin


class FileImporterMixin(PackageMixin):
    """Provide endpoints for easy file import -- both sync and async."""

    client: Steamship

    def __init__(self, client: Steamship):
        self.client = client

    @staticmethod
    def _async_importer_for_url(url: str) -> Optional[str]:
        """Return the async importer plugin, if necessary."""
        if "youtube.com" in url or "youtu.be" in url:
            return "youtube-transcript-importer"
        return None

    def _import_with_async_importer(
        self,
        url: str,
        importer_handle: str,
        mime_type: Optional[str] = None,
        tags: Optional[List[Tag]] = None,
    ) -> Tuple[File, Optional[Task]]:
        """Import a URL via an async FileImporter, returning a synchronous File but async import Task."""

        if ("youtube" in url or "youtu.be" in url) and mime_type is None:
            # Mark it as audio so that the s2t will work later.
            mime_type = MimeTypes.TXT

        file = File.create(self.client, tags=tags, mime_type=mime_type)

        if importer_handle is None:
            raise SteamshipError(
                message=f"Unable to async auto-guess file importer for {url} and none was provided."
            )

        file_importer = self.client.use_plugin(importer_handle)
        task = file.import_with_plugin(
            plugin_instance=file_importer.handle, url=url, mime_type=mime_type
        )
        file.add_or_update_tag(TagKind.STATUS, StatusTagName.IMPORTING)

        return file, task

    def _scrape_and_import_url(
        self,
        url: str,
        mime_type: Optional[str] = None,
        tags: Optional[List[Tag]] = None,
    ) -> Tuple[File, Optional[Task]]:
        """Scrape and then import the URL to a File, returning a synchronous File and no import Task."""
        if mime_type is None and ".pdf" in url:
            mime_type = MimeTypes.PDF

        response = requests.get(url)
        _bytes = response.content

        if not response.ok:
            msg = f"Error importing url {url}. Response was {response.text}"
            logging.error(msg)
            raise SteamshipError(message=msg)

        file = File.create(self.client, content=_bytes, mime_type=mime_type, tags=tags)
        return file, None

    def import_url_to_file_and_task(self, url: str) -> Tuple[File, Optional[Task]]:
        """Import the provided URL, returning the file and optional task, if async work is required."""
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)

        tags = [
            Tag(kind=DocTag.SOURCE, name=url),
            Tag(kind="_type", name="document"),
            Tag(kind="_index", name="not_index_yet"),
            Tag(kind=DocTag.TITLE, name=filename),
        ]

        if async_importer_for_url := self._async_importer_for_url(url):
            return self._import_with_async_importer(
                url, async_importer_for_url, tags=tags, mime_type=None
            )
        else:
            return self._scrape_and_import_url(url, tags=tags)

    @post("/import_url")
    def import_url(self, url: str) -> File:
        """Import the URL to a Steamship File. Actual import will be scheduled async."""
        file, task = self.import_url_to_file_and_task(url)
        return file

    @post("/import_text")
    def import_text(self, text: str, mime_type: Optional[str]) -> File:
        """Import the text to a Steamship File."""

        tags = [
            Tag(kind=DocTag.SOURCE, name="text"),
            Tag(kind="_type", name="document"),
            Tag(kind="_index", name="not_index_yet"),
        ]
        return File.create(self.client, content=text, mime_type=mime_type, tags=tags)
