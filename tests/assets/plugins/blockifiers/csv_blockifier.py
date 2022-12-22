"""CSV Blockifier - Steamship Plugin."""

import csv
import io
from typing import List, Optional, Type, Union

from pydantic import constr

from steamship.base import SteamshipError
from steamship.data.block import Block
from steamship.data.file import File
from steamship.data.tags import Tag
from steamship.invocable import Config, InvocableResponse, create_handler
from steamship.invocable.plugin_service import PluginRequest
from steamship.plugin.blockifier.blockifier import Blockifier
from steamship.plugin.inputs.raw_data_plugin_input import RawDataPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput


class CsvBlockifier(Blockifier):
    """Converts CSV or TSV into Tagged Steamship Blocks.

    A CSV file is mapped onto 1 File
    Each row in the CSV file is mapped onto a block
    Each block has text which is extracted from a single column
    Each block has one or more tags extracted from the values in one ore more columns
    """

    class CsvBlockifierConfig(Config):
        text_column: str
        tag_columns: List[str]
        tag_kind: str = None
        delimiter: Optional[str] = ","
        quotechar: Optional[constr(max_length=1)] = '"'
        escapechar: Optional[constr(max_length=1)] = "\\"
        newline: Optional[str] = "\\n"
        skipinitialspace: Optional[bool] = False

        def __init__(self, **kwargs):
            if isinstance(kwargs["tag_columns"], str):
                kwargs["tag_columns"] = kwargs["tag_columns"].split(",")
            super().__init__(**kwargs)

    def config_cls(self) -> Type[CsvBlockifierConfig]:
        return self.CsvBlockifierConfig

    def _get_text(self, row) -> str:
        text = row.get(self.config.text_column)
        if text:
            text = text.replace(self.config.newline, "\n")
        return text

    def _get_tags(self, row) -> List[str]:
        tag_values = []
        for tag_column in self.config.tag_columns:
            tag_value = row.get(tag_column)
            if tag_value:
                tag_values.append(tag_value.replace(self.config.newline, "\n"))
        return tag_values

    def run(
        self, request: PluginRequest[RawDataPluginInput]
    ) -> Union[InvocableResponse, InvocableResponse[BlockAndTagPluginOutput]]:
        if request is None or request.data is None or request.data.data is None:
            return InvocableResponse(
                error=SteamshipError(message="Missing data field on the incoming request.")
            )
        data = request.data.data  # TODO (enias): Simplify
        if isinstance(data, bytes):
            data = data.decode("utf-8")

        if not isinstance(data, str):
            return InvocableResponse(
                error=SteamshipError(message="The incoming data was not of expected String type")
            )

        reader = csv.DictReader(
            io.StringIO(data),
            delimiter=self.config.delimiter,
            quotechar=self.config.quotechar,
            escapechar=self.config.escapechar,
            skipinitialspace=self.config.skipinitialspace,
        )
        file = File.CreateRequest(blocks=[])
        for row in reader:
            text = self._get_text(row)
            tag_values = self._get_tags(row)

            block = Block(
                text=text,
                tags=[Tag(kind=self.config.tag_kind, name=tag_value) for tag_value in tag_values],
            )
            file.blocks.append(block)

        return InvocableResponse(data=BlockAndTagPluginOutput(file=file))


handler = create_handler(CsvBlockifier)
