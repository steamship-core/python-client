import logging
from io import BytesIO
from typing import Type
from zipfile import ZipFile

import requests

from steamship import DocTag, SteamshipError
from steamship.app import InvocableResponse, create_handler
from steamship.plugin.config import Config
from steamship.plugin.exporter import Exporter
from steamship.plugin.inputs.export_plugin_input import ExportPluginInput
from steamship.plugin.outputs.raw_data_plugin_output import RawDataPluginOutput
from steamship.plugin.service import PluginRequest

# If this isn't present, Localstack won't show logs
logging.getLogger().setLevel(logging.INFO)


class TestMarkdownExporter(Exporter):
    class EmptyConfig(Config):
        h1: str = DocTag.h1  # What to map to an H1
        h2: str = DocTag.h2  # What to map to an H2
        h3: str = DocTag.h3  # What to map to an H3
        h4: str = DocTag.h4  # What to map to an H4
        h5: str = DocTag.h5  # What to map to an H5
        p: str = DocTag.p  # What to map to a P
        list_item: str = DocTag.list_item  # What to map to an LI
        link: str = DocTag.link  # What to map to an LINK
        strong: str = DocTag.strong  # What to map to STRONG
        emph: str = DocTag.emph  # What to map to EMPH

    def config_cls(self) -> Type[Config]:
        return self.EmptyConfig

    def run(
        self, request: PluginRequest[ExportPluginInput]
    ) -> InvocableResponse[RawDataPluginOutput]:
        logging.info(f"Inside parser: {type(request)}")

        if not request.data:
            raise SteamshipError(message="Missing the `data` field of the Request object.")
        if not request.data.data_url:
            raise SteamshipError(message="Missing the `data_url` field of the ExportPluginInput.")
        if not request.data.filename:
            raise SteamshipError(message="Missing the `filename` field of the ExportPluginInput.")

        # Download the data.
        file_resp = requests.get(request.data.data_url)
        myzip = ZipFile(BytesIO(file_resp.read()))

        # Now we open the file
        output_str = ""
        for line in myzip.open(request.data.filename).readlines():
            line_str = line.decode("utf-8")
            output_str += line_str
            print(line_str)

        return RawDataPluginOutput(string=line_str)


handler = create_handler(TestMarkdownExporter)
