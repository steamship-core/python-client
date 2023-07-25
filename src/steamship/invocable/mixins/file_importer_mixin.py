import logging
import os
from typing import List, Optional, Tuple, Union
from urllib.parse import urlparse

import requests
from pydantic import AnyUrl

from steamship import File, MimeTypes, SteamshipError, Tag, Task
from steamship.invocable import post
from steamship.invocable.mixins import FileType, metadata_to_tags
from steamship.invocable.package_mixin import PackageMixin


class FileImporterMixin(PackageMixin):
    """Provide endpoints for easy file import -- both sync and async."""

    def _import_with_async_importer(
        self,
        url: str,
        importer_handle: str,
        mime_type: MimeTypes,
        tags: Optional[List[Tag]] = None,
    ) -> Tuple[File, Optional[Task]]:
        file = File.create(self.client, tags=tags, mime_type=mime_type)

        if importer_handle is None:
            raise SteamshipError(
                message=f"Unable to async auto-guess file importer for {url} and none was provided."
            )

        file_importer = self.client.use_plugin(importer_handle)
        task = file.import_with_plugin(
            plugin_instance=file_importer.handle, url=url, mime_type=mime_type
        )
        file.add_or_update_metadata("status", "Importing")
        return file, task

    def _scrape_and_import_url(
        self,
        url: str,
        mime_type: MimeTypes,
        tags: Optional[List[Tag]] = None,
    ) -> Tuple[File, Optional[Task]]:
        """Scrape and then import the URL to a File, returning a synchronous File and no import Task."""

        response = requests.get(url)
        _bytes = response.content

        if not response.ok:
            msg = f"Error importing url {url}. Response was {response.text}"
            logging.error(msg)
            raise SteamshipError(message=msg)

        file = File.create(self.client, content=_bytes, mime_type=mime_type, tags=tags)
        return file, None

    @post("/import_url")
    def import_url(self, url: str) -> File:
        """Import the URL to a Steamship File. Actual import will be scheduled async."""
        file, _ = self.import_content(
            content_or_url=url,
        )
        return file

    @post("/import_text")
    def import_text(self, text: str, mime_type: Optional[str] = None) -> File:
        """Import the text to a Steamship File."""
        file, _ = self.import_content(
            content_or_url=text,
            file_type=FileType.TEXT,
            mime_type=mime_type,
        )
        return file

    @staticmethod
    def is_youtube(url: str) -> bool:
        """Return the async importer plugin, if necessary."""
        return "youtube.com" in url or "youtu.be" in url

    @post("import")
    def import_content(
        self,
        content_or_url: Union[str, AnyUrl],
        file_type: Optional[FileType] = None,
        metadata: Optional[dict] = None,
        mime_type: Optional[str] = None,
    ) -> Tuple[File, Optional[Task]]:

        metadata = metadata or {}
        metadata["_type"] = "document"  # File = Document
        metadata["_index"] = "not_indexed_yet"

        task = None
        if file_type == FileType.YOUTUBE or self.is_youtube(content_or_url):
            metadata["source"] = metadata.get("source", content_or_url)
            metadata["mime_type"] = MimeTypes.TXT
            file, task = self._import_with_async_importer(
                content_or_url,
                "youtube-transcript-importer",
                tags=metadata_to_tags(metadata),
                mime_type=MimeTypes.TXT,
            )
        elif file_type == FileType.TEXT:
            metadata["source"] = metadata.get("source", "local")
            metadata["mime_type"] = MimeTypes.TXT
            file = File.create(
                self.client,
                content=content_or_url,
                mime_type=mime_type,
                tags=metadata_to_tags(metadata),
            )
        elif file_type == FileType.PDF or (
            file_type is None and (".pdf" in content_or_url or mime_type == FileType.PDF)
        ):
            parsed_url = urlparse(content_or_url)
            filename = os.path.basename(parsed_url.path)
            metadata["source"] = metadata.get("source", content_or_url)
            metadata["filename"] = metadata.get("filename", filename)
            metadata["mime_type"] = MimeTypes.PDF
            file, task = self._scrape_and_import_url(
                content_or_url,
                tags=metadata_to_tags(metadata),
                mime_type=mime_type or MimeTypes.PDF,
            )
        elif file_type == FileType.WEB:
            metadata["source"] = metadata.get("source", content_or_url)
            raise NotImplementedError()
        else:
            raise NotImplementedError()

        return file, task
