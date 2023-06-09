from typing import Optional

from steamship import File, MimeTypes, Steamship, SteamshipError, Task
from steamship.invocable import post
from steamship.invocable.package_mixin import PackageMixin
from steamship.utils.file_tags import update_file_status


class BlockifierMixin(PackageMixin):
    """Provides endpoints for easy Blockification of files."""

    client: Steamship

    def __init__(self, client: Steamship):
        self.client = client

    @post("/blockify_file")
    def blockify(
        self,
        file_id: str,
        mime_type: Optional[MimeTypes] = None,
        blockifier_handle: Optional[str] = None,
        after_task_id: Optional[str] = None,
    ) -> Task:
        """Blockify the file `file_id` using a curated set of defaults for the provided `mime_type`.

        If no MIME Type is provided, the file's recorded MIME Type will be used.
        If still no MIME Type is available, an error will be thrown.

        Supported MIME Types:

        - PDF
        - Audio (MP3, MP4, WEBM)
        """

        file = File.get(self.client, _id=file_id)
        update_file_status(self.client, file, "Blockifying")

        _mime_type = mime_type or file.mime_type
        if not _mime_type:
            raise SteamshipError(
                message=f"No MIME Type found for file {file.id}. Unable to blockify."
            )

        plugin_instance = None

        if blockifier_handle:
            plugin_instance = self.client.use_plugin(blockifier_handle)
        elif _mime_type == MimeTypes.PDF:
            plugin_instance = self.client.use_plugin("pdf-blockifier")
        elif _mime_type in [MimeTypes.MP3, MimeTypes.MP4_AUDIO, MimeTypes.WEBM_AUDIO]:
            plugin_instance = self.client.use_plugin("s2t-blockifier-default")
        elif _mime_type in [MimeTypes.MKD, MimeTypes.TXT]:
            plugin_instance = self.client.use_plugin("markdown-blockifier-default")

        if not plugin_instance:
            raise SteamshipError(
                message=f"Unable to blockify file {file.id}. MIME Type {_mime_type} unsupported"
            )

        # Postpone the operation if required.
        wait_on_tasks = []
        if after_task_id:
            wait_on_tasks.append(Task(client=self.client, task_id=after_task_id))

        return file.blockify(plugin_instance.handle, wait_on_tasks=wait_on_tasks)
