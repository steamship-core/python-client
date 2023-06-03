from typing import Optional, Tuple

import requests

from steamship import File, MimeTypes, Steamship, SteamshipError, Task
from steamship.agents import logging
from steamship.invocable import post
from steamship.invocable.package_mixin import PackageMixin


class FileImporterMixin(PackageMixin):
    """Provide endpoints for easy file import -- both sync and async."""

    client: Steamship

    def __init__(self, client: Steamship):
        self.client = client

    def _async_importer_for_url(self, url: str) -> Optional[str]:
        """Return the async importer plugin, if necessary."""
        if "youtube.com" in url or "youtu.be" in url:
            return "youtube-file-importer"
        return None

    def _import_with_async_importer(
        self,
        url: str,
        importer_handle: str,
        mime_type: Optional[str] = None,
    ) -> Tuple[File, Optional[Task]]:
        """Import a URL via an async FileImporter, returning a synchronous File but async import Task."""
        file = File.create(self.client)

        if importer_handle is None:
            raise SteamshipError(
                message=f"Unable to async auto-guess file importer for {url} and none was provided."
            )

        file_importer = self.client.use_plugin(importer_handle)
        task = file.import_with_plugin(
            plugin_instance=file_importer.handle, url=url, mime_type=mime_type
        )
        return file, task

    def _scrape_and_import_url(
        self, url: str, mime_type: Optional[str] = None
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

        file = File.create(self.client, content=_bytes, mime_type=mime_type)
        return file, None

    def import_url_to_file_and_task(self, url: str) -> Tuple[File, Optional[Task]]:
        """Import the provided URL, returning the file and optional task, if async work is required."""
        async_importer_for_url = self._async_importer_for_url(url)
        if async_importer_for_url:
            return self._import_with_async_importer(url, async_importer_for_url, mime_type=None)
        else:
            return self._scrape_and_import_url(url)

    @post("/import_url")
    def import_url(self, url: str) -> File:
        """Import the URL to a Steamship File. Actual import will be scheduled Async."""
        file, task = self.import_url_to_file_and_task(url)
        return file

    @post("/import_text")
    def import_text(self, text: str, mime_type: Optional[str]) -> File:
        """Import the text to a Steamship File."""
        return File.create(self.client, content=text, mime_type=mime_type)
