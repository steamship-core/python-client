"""Blockifies a file using a best effort guess based on mime-type."""
from typing import Optional

from steamship import MimeTypes, SteamshipError, Task
from steamship.data.file import File


def blockify(file: File, mime_type: Optional[MimeTypes] = None) -> Task:
    """Scrape a file via URL, returning a File object no matter what."""

    _mime_type = mime_type or file.mime_type
    if not _mime_type:
        raise SteamshipError(
            message=f"No MIME Type was found for file {file.id}. Unable to easy-blockify"
        )

    if _mime_type == MimeTypes.PDF:
        plugin_instance = file.client.use_plugin("pdf-blockifier")
    elif _mime_type in [MimeTypes.MP3, MimeTypes.MP4_AUDIO, MimeTypes.WEBM_AUDIO]:
        plugin_instance = file.client.use_plugin("s2t-blockifier-default")
    elif _mime_type in [MimeTypes.MKD, MimeTypes.TXT]:
        plugin_instance = file.client.use_plugin("markdown-blockifier-default")
    else:
        raise SteamshipError(
            message=f"Unable to easy.blockfy file of MIME type {mime_type}. File ID was {file.id}"
        )

    return file.blockify(plugin_instance.handle)
