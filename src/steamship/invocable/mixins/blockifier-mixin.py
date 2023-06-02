from typing import Optional

import requests
from pydantic import HttpUrl

from steamship import File, MimeTypes, Steamship, SteamshipError, Tag, Task
from steamship.invocable import post


class BlockifiersMixin:
    """Provides endpoints for easy 'Blockification' of files."""

    client: Steamship

    def __init__(self, client: Steamship, index_handle: str = "default"):
        self.client = client
        self.index_name = index_handle

    def _blockify(self, file: File, mime_type: Optional[MimeTypes] = None) -> Task:
        """Scrape a file via URL, returning a File object no matter what."""

        _mime_type = mime_type or file.mime_type
        if not _mime_type:
            raise SteamshipError(
                message=f"No MIME Type found for file {file.id}. Unable to blockify."
            )

        if _mime_type == MimeTypes.PDF:
            plugin_instance = self.client.use_plugin("pdf-blockifier")
        elif _mime_type in [MimeTypes.MP3, MimeTypes.MP4_AUDIO, MimeTypes.WEBM_AUDIO]:
            plugin_instance = self.client.use_plugin("s2t-blockifier-default")
        elif _mime_type in [MimeTypes.MKD, MimeTypes.TXT]:
            plugin_instance = self.client.use_plugin("markdown-blockifier-default")
        else:
            raise SteamshipError(
                message=f"Unable to blockify file {file.id}. MIME Type {_mime_type} unsupported"
            )

        return file.blockify(plugin_instance.handle)

    def _import_youtube_url(self, youtube_url: HttpUrl) -> Task:
        file_importer = self.client.use_plugin("youtube-file-importer")
        file_create_task = File.create_with_plugin(
            self.client, plugin_instance=file_importer.handle, url=youtube_url
        )
        return self.invoke_later(
            method="transcribe_lecture",
            arguments={"task_id": file_create_task.task_id, "source": youtube_url},
            wait_on_tasks=[file_create_task],
        )

    def _import_pdf_url(self, pdf_url: HttpUrl) -> Task:
        response = requests.get(pdf_url)
        file = File.create(self.client, content=response.content, mime_type=MimeTypes.PDF)

        # Hacky way to get the last segment of the URL but drop the query & hash
        title = pdf_url.split("/")[-1]
        title = title.split("?")[0]
        title = title.split("#")[0]

        # Tag the title for provenance reporting
        Tag.create(self.client, file_id=file.id, kind="source", name=pdf_url)
        Tag.create(self.client, file_id=file.id, kind="title", name=title)

        return self.invoke_later(
            method="blockify_pdf",
            arguments={"file_id": file.id, "source": pdf_url},
        )

    def _blockify_pdf(self, file: File, source: str):
        """Enqueue an async Blockify task for `file_id`."""
        self._update_file_status(file, "Parsing")
        blockifier = self.client.use_plugin("pdf-blockifier")
        blockify_file_task = file.blockify(blockifier.handle)
        return self.invoke_later(
            method="index_pdf",
            arguments={"file_id": file_id, "source": source},
            wait_on_tasks=[blockify_file_task],
        )

    def _blockify_audio(self, file: File, source: str):
        """Enqueue an async Blockify task for `file_id`."""
        self._update_file_status(file, "Parsing")
        blockifier = self.client.use_plugin("pdf-blockifier")
        blockify_file_task = file.blockify(blockifier.handle)
        return self.invoke_later(
            method="index_pdf",
            arguments={"file_id": file_id, "source": source},
            wait_on_tasks=[blockify_file_task],
        )

    def _blockify_markdown(self, file: File, source: str):
        """Enqueue an async Blockify task for `file_id`."""
        self._update_file_status(file, "Parsing")
        blockifier = self.client.use_plugin("markdown-blockifier-default")
        blockify_file_task = file.blockify(blockifier.handle)
        return self.invoke_later(
            method="index_pdf",
            arguments={"file_id": file_id, "source": source},
            wait_on_tasks=[blockify_file_task],
        )

    @post("/blockify_video")
    def blockify_video(self, task_id: str, source: str):
        file_create_task = Task.get(self.client, task_id)
        file = File.get(self.client, json.loads(file_create_task.output)["file"]["id"])

        Tag.create(self.client, file_id=file.id, kind="source", name=source)
        try:
            Tag.create(self.client, file_id=file.id, kind="title", name=YouTube(source).title)
        except Exception as e:
            logging.warning(f"Unable to access title of YouTube video {e}")
            Tag.create(self.client, file_id=file.id, kind="title", name=source)

        self._update_file_status(file, "Transcribing")

        blockifier = self.client.use_plugin("s2t-blockifier-default")
        blockify_file_task = file.blockify(blockifier.handle)

        return self.invoke_later(
            method="index_lecture",
            arguments={"file_id": file.id, "source": source},
            wait_on_tasks=[blockify_file_task],
        )

    @post("/blockify_file")
    def blockify_file(self, file_id: str, mime_type: Optional[str] = None) -> Task:
        """Blockify the file `file_id` using a curated set of defaults for the provided `mime_type`.

        If no MIME Type is provided, the file's recorded MIME Type will be used.
        If still no MIME Type is available, an error will be thrown.

        Supported MIME Types:

        - PDF
        - Audio (MP3, MP4, WEBM)
        """

        file = File.get(self.client, _id=file_id)
        return self._blockify(file, mime_type)
