import logging
import tempfile
from pathlib import Path
from typing import ClassVar, Optional

from steamship import Steamship, SteamshipError
from steamship.base.client import Client
from steamship.base.model import CamelModel
from steamship.data.workspace import SignedUrl, Workspace
from steamship.utils.signed_urls import download_from_signed_url, upload_to_signed_url
from steamship.utils.zip_archives import unzip_folder, zip_folder


class ModelCheckpoint(CamelModel):
    # The default model checkpoint handle unless one is provided.
    DEFAULT_HANDLE: ClassVar[str] = "default"

    """Represents the saved state of a trained PluginInstance.
    """
    client: Client
    workspace: Optional[Workspace] = None
    plugin_instance_id: str

    parent_directory: Optional[Path] = None  # e.g. /tmp
    handle: str = None  # The handle of this ModelCheckpoint.
    plugin_instance_id: str = None  #

    def __init__(
        self,
        client: Steamship,
        parent_directory: Optional[Path] = None,
        handle: str = DEFAULT_HANDLE,
        plugin_instance_id: str = None,
    ):
        super().__init__(
            client=client,
            parent_directory=parent_directory,
            plugin_instance_id=plugin_instance_id,
            handle=handle or ModelCheckpoint.DEFAULT_HANDLE,
        )

        if self.plugin_instance_id is None:
            raise SteamshipError("Null plugin_instance_id provided ModelCheckpoint")

        self.workspace = client.get_workspace()

        if parent_directory is None:
            # TODO(ted): We may want to not use a tempdir so that we can cache it.
            self.parent_directory = Path(tempfile.mkdtemp())

        # Create the folder path on disk.
        logging.info(f"Making sure Checkpoint path exists: {self.folder_path_on_disk()}")
        self.folder_path_on_disk().mkdir(parents=True, exist_ok=True)

    def folder_path_on_disk(self) -> Path:
        """Returns the path to this checkpoint on the local disk.

        On disk, the model checkpoint is the folder:
            `{parent_directory}/{checkpoint_handle}/`
        """
        return self.parent_directory / Path(self.handle)

    def archive_path_on_disk(self) -> Path:
        """Returns the path to the checkpoint archive on disk.

        On disk, the model checkpoint is the folder:
            `{parent_directory}/{checkpoint_handle}.zip`
        """
        return self.parent_directory / Path(f"{self.handle}.zip")

    def archive_path_in_steamship(self, as_handle: str = None) -> str:
        """Returns the path to the checkpoint archive on Steamship.

        On steamship, the checkpoint is archived in the Workspace's PluginInstance bucket as:
        `{plugin_instance_bucket}/{plugin_instance_id}/{checkpoint_handle}.zip`

        Here we only return the following path since the bucket is specified separately
        in the required Steamship API calls: `{plugin_instance_id}/{checkpoint_handle}.zip`
        """
        return f"{self.plugin_instance_id}/{as_handle or self.handle}.zip"

    def download_model_bundle(self) -> Path:
        """Download's the model from Steamship and unzips to `parent_directory`"""
        download_resp = self.workspace.create_signed_url(
            SignedUrl.Request(
                bucket=SignedUrl.Bucket.PLUGIN_DATA,
                filepath=self.archive_path_in_steamship(),
                operation=SignedUrl.Operation.READ,
            )
        )
        if not download_resp or not download_resp.signed_url:
            raise SteamshipError(
                message=f"Received empty Signed URL for model download of '{self.handle}."
            )
        download_from_signed_url(download_resp.signed_url, to_file=self.archive_path_on_disk())
        unzip_folder(self.archive_path_on_disk(), into_folder=self.folder_path_on_disk())
        if not download_resp or not download_resp.signed_url:
            raise SteamshipError(
                message=f"Received empty Signed URL for model download of '{self.handle}."
            )
        download_from_signed_url(download_resp.signed_url, to_file=self.archive_path_on_disk())
        unzip_folder(self.archive_path_on_disk(), into_folder=self.folder_path_on_disk())
        return self.folder_path_on_disk()

    def _upload_model_zip(self, as_handle: str = None):
        """Assumes a pre-zipped model, uploads to the requested zip.

        This is an internal function. Please use upload_model_bundle as an caller."""
        logging.info(f"ModelCheckpoint:_upload_model_zip - handle={as_handle}")
        signed_url_resp = self.workspace.create_signed_url(
            SignedUrl.Request(
                bucket=SignedUrl.Bucket.PLUGIN_DATA,
                filepath=self.archive_path_in_steamship(as_handle=as_handle),
                operation=SignedUrl.Operation.WRITE,
            )
        )

        if not signed_url_resp:
            raise SteamshipError(
                message="Empty result on Signed URL request while uploading model checkpoint"
            )
        if not signed_url_resp.signed_url:
            raise SteamshipError(
                message="Empty signedUrl on Signed URL request while uploading model checkpoint"
            )

        upload_to_signed_url(signed_url_resp.signed_url, filepath=self.archive_path_on_disk())

    def upload_model_bundle(self, set_as_default: bool = True):
        """Zips and uploads the Model to steamship"""
        logging.info("ModelCheckpoint:upload_model_bundle")
        zip_folder(self.folder_path_on_disk(), into_file=self.archive_path_on_disk())
        self._upload_model_zip()

        if set_as_default:
            # For simplicity, we'll assume the checkpoint named `default` is the one to be loaded unless otherwise
            # specified. This means that we need to double-upload some checkpoints:
            # - Once under the actual checkpoint name (e.g. `epoch-10`)
            # - Again under the name: default
            self._upload_model_zip(as_handle=ModelCheckpoint.DEFAULT_HANDLE)
