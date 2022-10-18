from typing import Type

from steamship import SteamshipError
from steamship.invocable import InvocableResponse, create_handler
from steamship.invocable.plugin_service import PluginRequest
from steamship.plugin.config import Config
from steamship.plugin.file_importer import FileImporter
from steamship.plugin.inputs.file_import_plugin_input import FileImportPluginInput
from steamship.plugin.outputs.raw_data_plugin_output import RawDataPluginOutput


class TestFileImporterSteamshipErrorPlugin(FileImporter):
    class EmptyConfig(Config):
        pass

    def config_cls(self) -> Type[Config]:
        return self.EmptyConfig

    def run(
        self, request: PluginRequest[FileImportPluginInput]
    ) -> InvocableResponse[RawDataPluginOutput]:
        raise SteamshipError(message="TestFileImporterSteamshipErrorPlugin")


handler = create_handler(TestFileImporterSteamshipErrorPlugin)
