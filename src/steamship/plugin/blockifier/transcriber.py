from abc import abstractmethod
from typing import List, Optional, Set

from steamship import Block, File, SteamshipError, Tag
from steamship.base.mime_types import MimeTypes
from steamship.invocable import InvocableResponse
from steamship.invocable.plugin_service import PluginRequest
from steamship.plugin.blockifier.blockifier import Blockifier
from steamship.plugin.inputs.raw_data_plugin_input import RawDataPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput


class Transcriber(Blockifier):
    @abstractmethod
    def transcribe(
        self, audio_file: PluginRequest[RawDataPluginInput], mime_type: MimeTypes
    ) -> (str, Optional[List[Tag]]):
        """Transcribe an audio file and turn it into a transcription and optional Tags."""
        raise NotImplementedError()

    @abstractmethod
    def supported_mime_types(self) -> Set[MimeTypes]:
        raise NotImplementedError()

    def run(
        self, request: PluginRequest[RawDataPluginInput]
    ) -> InvocableResponse[BlockAndTagPluginOutput]:
        supported_mime_types = self.supported_mime_types()
        if request.data.default_mime_type not in supported_mime_types:
            raise SteamshipError(
                "Unsupported mimeType. "
                f"The following mimeTypes are supported: {supported_mime_types}"
            )

        transcription, tags = self.transcribe(
            audio_file=request.data.data, mime_type=request.data.default_mime_type
        )
        return InvocableResponse(
            data=BlockAndTagPluginOutput(
                file=File(
                    blocks=[
                        Block(
                            text=transcription,
                            tags=tags,
                        )
                    ]
                )
            )
        )
