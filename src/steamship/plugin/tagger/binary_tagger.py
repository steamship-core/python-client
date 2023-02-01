import uuid
from abc import ABC, abstractmethod
from typing import List

from steamship import SteamshipError, Tag
from steamship.data import TagValueKey
from steamship.data.workspace import SignedUrl
from steamship.invocable import InvocableResponse, post
from steamship.invocable.plugin_service import PluginService
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.request import PluginRequest
from steamship.utils.signed_urls import upload_to_signed_url


class BinaryGenerator(PluginService[BlockAndTagPluginInput, BlockAndTagPluginOutput], ABC):
    """Superclass for Taggers which return a binary value based each block's text, to be stored within the Workspace."""

    def run(
        self, request: PluginRequest[BlockAndTagPluginInput]
    ) -> InvocableResponse[BlockAndTagPluginOutput]:
        """Run the binary generator on each block of text."""

        file = request.data.file
        workspace = self.client.get_workspace()

        for block in request.data.file.blocks:
            generated_bytes_and_tags = self.generate_binary_and_tag(block.text)
            for _bytes, tag in generated_bytes_and_tags:

                # Remote filename
                remote_filename = uuid.uuid4()

                # Put it in the generated output
                signed_url_resp = workspace.create_signed_url(
                    SignedUrl.Request(
                        bucket=SignedUrl.Bucket.PLUGIN_DATA,
                        filepath=remote_filename,
                        operation=SignedUrl.Operation.WRITE,
                    )
                )

                if not signed_url_resp:
                    raise SteamshipError(
                        message="Empty result on Signed URL request while uploading generated asset."
                    )
                if not signed_url_resp.signed_url:
                    raise SteamshipError(
                        message="Empty signedUrl on Signed URL request while uploading generated asset"
                    )

                upload_to_signed_url(signed_url_resp.signed_url, _bytes=_bytes)

                download_resp = self.workspace.create_signed_url(
                    SignedUrl.Request(
                        bucket=SignedUrl.Bucket.PLUGIN_DATA,
                        filepath=remote_filename,
                        operation=SignedUrl.Operation.READ,
                    )
                )
                if not download_resp or not download_resp.signed_url:
                    raise SteamshipError(message="Received empty Signed URL for binary download.")

                tag.value[TagValueKey.URL_VALUE] = download_resp.signed_url
                block.tags.append(tag)

        return InvocableResponse(data=BlockAndTagPluginOutput(file=file))

    @abstractmethod
    def generate_binary_and_tag(self, text: str) -> List[tuple[bytes, Tag]]:
        raise NotImplementedError()

    @post("tag")
    def run_endpoint(self, **kwargs) -> InvocableResponse[BlockAndTagPluginOutput]:
        """Exposes the Tagger's `run` operation to the Steamship Engine via the expected HTTP path POST /tag"""
        return self.run(PluginRequest[BlockAndTagPluginInput].parse_obj(kwargs))
