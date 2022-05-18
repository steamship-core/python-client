import dataclasses
import os
import tempfile
from pathlib import Path
from typing import Optional

from steamship import SteamshipError
from steamship.base import Client
from steamship.data.space import SignedUrl, Space
from steamship.utils.signed_urls import download_from_signed_url, upload_to_signed_url
from steamship.utils.zip_archives import unzip_folder, zip_folder


def _get_space(client: Client) -> Space:
    # We should probably add a hard-coded tway to get this. The client in a Steamship Plugin/App comes
    # pre-configured with an API key and the Space in which this client should be operating.
    # This is a way to load the model object for that space.
    space = Space.get(client, id_=client.config.space_id, handle=client.config.space_handle)
    if not space.data:
        raise SteamshipError(
            message="Error while retrieving the Space associated with this client config.",
            internal_message=f"space_id={client.config.space_id}   space_handle={client.config.space_handle}",
        )
    return space.data


@dataclasses.dataclass
class ModelCheckpoint:
    # The default model checkpoint handle unless one is provided.
    DEFAULT_HANDLE = "default"

    """Represents the saved state of a trained PluginInstance.
    """
    client: Client
    space: Space
    plugin_instance_id: str

    parent_directory: Optional[Path] = None  # e.g. /tmp
    handle: str = None  # The handle of this ModelCheckpoint.
    plugin_instance_id: str = None  #

    def __init__(
        self,
        client: Client,
        parent_directory: Optional[Path] = None,
        handle: str = DEFAULT_HANDLE,
        plugin_instance_id: str = None,
    ):
        self.client = client
        self.parent_directory = parent_directory
        self.plugin_instance_id = plugin_instance_id
        self.handle = handle or ModelCheckpoint.DEFAULT_HANDLE

        if self.plugin_instance_id is None:
            raise SteamshipError("Null plugin_instance_id provided ModelCheckpoint")

        # Load the space that we're operating within.
        self.space = _get_space(client)

        if parent_directory is None:
            # TODO(ted): We may want to not use a tempdir so that we can cache it.
            self.parent_directory = Path(tempfile.mkdtemp())

        # Create the folder path on disk.
        os.makedirs(str(self.folder_path_on_disk()))

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

        On steamship, the checkpoint is archived in the Space's PluginInstance bucket as:
           `{plugin_instance_bucket}/{plugin_instance_id}/{checkpoint_handle}.zip

        Here we only return the following path since the bucket is specified separately
        in the required Steamship API calls:
            `{plugin_instance_id}/{checkpoint_handle}.zip`
        """
        return f"{self.plugin_instance_id}/{as_handle or self.handle}.zip"

    def download_model_bundle(self) -> Path:
        """Download's the model from Steamship and unzips to `parent_directory`"""
        download_resp = self.space.create_signed_url(
            SignedUrl.Request(
                bucket=SignedUrl.Bucket.pluginData,
                filepath=self.archive_path_in_steamship(),
                operation=SignedUrl.Operation.read,
            )
        )
        if not download_resp.data or not download_resp.data.signedUrl:
            raise SteamshipError(
                message=f"Received empty Signed URL for model download of '{self.handle}."
            )
        download_from_signed_url(download_resp.data.signedUrl, to_file=self.archive_path_on_disk())
        unzip_folder(self.archive_path_on_disk(), into_folder=self.folder_path_on_disk())
        return self.folder_path_on_disk()

    def _upload_model_zip(self, as_handle: str = None):
        """Assumes a pre-zipped model, uploads to the requested zip.

        This is an internal function. Please use upload_model_bundle as an caller."""
        signed_url_resp = self.space.create_signed_url(
            SignedUrl.Request(
                bucket=SignedUrl.Bucket.pluginData,
                filepath=self.archive_path_in_steamship(as_handle=as_handle),
                operation=SignedUrl.Operation.write,
            )
        )

        if signed_url_resp.error:
            raise signed_url_resp.error
        if not signed_url_resp.data:
            raise SteamshipError(
                message="Empty result on Signed URL request while uploading model checkpoint"
            )
        if not signed_url_resp.data.signedUrl:
            raise SteamshipError(
                message="Empty signedUrl on Signed URL request while uploading model checkpoint"
            )

        upload_to_signed_url(signed_url_resp.data.signedUrl, filepath=self.archive_path_on_disk())

    def upload_model_bundle(self, set_as_default: bool = True):
        """Zips and uploads the Model to steamship"""

        zip_folder(self.folder_path_on_disk(), into_file=self.archive_path_on_disk())
        self._upload_model_zip()

        if set_as_default:
            # For simplicity, we'll assume the checkpoint named `default` is the one to be loaded unless otherwise
            # specified. This means that we need to double-upload some checkpoints:
            # - Once under the actual checkpoint name (e.g. `epoch-10`)
            # - Again under the name: default
            self._upload_model_zip(as_handle=ModelCheckpoint.DEFAULT_HANDLE)
