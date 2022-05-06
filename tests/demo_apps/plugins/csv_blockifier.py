"""CSV Blockifier - Steamship Plugin."""

import csv
import io
from typing import Union, List, Dict, Optional

from pydantic import BaseModel, constr

from steamship.base.error import SteamshipError
from steamship.data.block import Block
from steamship.data.file import File
from steamship.data.tags import Tag
from steamship.deployable import Deployable, post, create_handler, Response
from steamship.plugin.blockifier import Blockifier
from steamship.plugin.inputs.raw_data_plugin_input import RawDataPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.service import PluginRequest


class Config(BaseModel):
    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v}
        super().__init__(**kwargs)


class CsvBlockifierConfig(Config):
    textColumn: str  # TODO: Make pep8 compatible once the engine allows it
    tagColumns: List[str]
    delimiter: Optional[str] = ","
    quotechar: Optional[constr(max_length=1)] = '"'
    escapechar: Optional[constr(max_length=1)] = "\\"
    newline: Optional[str] = "\\n"
    skipinitialspace: Optional[bool] = False
    tagKind: Optional[str] = None

    def __init__(self, **kwargs):
        if isinstance(kwargs["tagColumns"], str):
            kwargs["tagColumns"] = kwargs["tagColumns"].split(",")
        super().__init__(**kwargs)


class CsvBlockifier(Blockifier, Deployable):
    """Converts CSV or TSV into Tagged Steamship Blocks.

    A CSV file is mapped onto 1 File
    Each row in the CSV file is mapped onto a block
    Each block has text which is extracted from a single column
    Each block has one or more tags extracted from the values in one ore more columns
    """

    def __init__(self, client=None, config: Dict[str, any] = None):
        super().__init__()
        self.config = CsvBlockifierConfig(**config)

    def _get_text(self, row) -> str:
        text = row.get(self.config.textColumn)
        if text:
            text = text.replace(self.config.newline, "\n")
        return text

    def _get_tags(self, row) -> List[str]:
        tag_values = []
        for tag_column in self.config.tagColumns:
            tag_value = row.get(tag_column)
            if tag_value:
                tag_values.append(tag_value.replace(self.config.newline, "\n"))
        return tag_values

    def run(
        self, request: PluginRequest[RawDataPluginInput]
    ) -> Union[Response, Response[BlockAndTagPluginOutput]]:
        if request is None or request.data is None or request.data.data is None:
            return Response(
                error=SteamshipError(
                    message="Missing data field on the incoming request."
                )
            )
        data = request.data.data
        if isinstance(data, bytes):
            data = data.decode("utf-8")

        if type(data) != str:
            return Response(
                error=SteamshipError(
                    message="The incoming data was not of expected String type"
                )
            )

        reader = csv.DictReader(
            io.StringIO(data),
            delimiter=self.config.delimiter,
            quotechar=self.config.quotechar,
            escapechar=self.config.escapechar,
            skipinitialspace=self.config.skipinitialspace,
        )
        file = File(blocks=[])
        for row in reader:
            text = self._get_text(row)
            tag_values = self._get_tags(row)

            block = Block.CreateRequest(
                text=text,
                tags=[
                    Tag.CreateRequest(kind=self.config.tagKind, name=tag_value)
                    for tag_value in tag_values
                ],
            )
            file.blocks.append(block)

        return Response(data=BlockAndTagPluginOutput(file=file))

    @post("blockify")
    def blockify(self, **kwargs) -> Response:
        """App endpoint for our plugin.

        The `run` method above implements the Plugin interface for a Converter.
        This `convert` method exposes it over an HTTP endpoint as a Steamship App.

        When developing your own plugin, you can almost always leave the below code unchanged.
        """
        blockify_request = Blockifier.parse_request(request=kwargs)
        return self.run(blockify_request)


handler = create_handler(CsvBlockifier)
