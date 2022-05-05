"""CSV Blockifier - Steamship Plugin."""

import csv
import io
from typing import Union, List, Dict, Optional

from pydantic import BaseModel, constr
from steamship.app import App, post, create_handler, Response
from steamship.base.error import SteamshipError
from steamship.data.block import Block
from steamship.data.file import File
from steamship.data.tags import Tag
from steamship.plugin.blockifier import Blockifier
from steamship.plugin.inputs.raw_data_plugin_input import RawDataPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.service import PluginRequest


class Config(BaseModel):
    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v}
        super().__init__(**kwargs)


class CsvBlockifierConfig(Config):
    textColumn: str  # TODO: Make pep8 compatible once version_config is changed
    tagColumns: List[str]  # TODO: This should be a list?
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


class CsvBlockifier(Blockifier, App):
    """ "Converts CSV or TSV into Tagged Steamship Blocks.

    Rows = Blocks
    TODO: Q: What is I want to search based on AI generated tags, and non ai generated tags?
    """

    # TODO: Dangerous: We require client to be available, but this is never enforces
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

        data = request.data.data  # TODO: This is weird, why two levels?
        if isinstance(data, bytes):
            data = data.decode("utf-8")

        if type(data) != str:
            # TODO: I feel like we should allow developers to raise Exceptions, we catch them and wrap them in responses ourselves.
            # Inspiration: FastAPI
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
            # TODO: Why does a Tag have a value and a value? Why are we not adding the value of the tag to the value field
            file.blocks.append(block)

        return Response(data=BlockAndTagPluginOutput(file=file))

    @post(
        "blockify"
    )  # TODO: Q: Do we have to be specific or can plugins just operate using a "run" endpoint
    def blockify(self, **kwargs) -> Response:
        """App endpoint for our plugin.

        The `run` method above implements the Plugin interface for a Converter.
        This `convert` method exposes it over an HTTP endpoint as a Steamship App.

        When developing your own plugin, you can almost always leave the below code unchanged.
        """
        blockify_request = Blockifier.parse_request(request=kwargs)
        return self.run(blockify_request)


handler = create_handler(CsvBlockifier)  # Risky to require you to write this
