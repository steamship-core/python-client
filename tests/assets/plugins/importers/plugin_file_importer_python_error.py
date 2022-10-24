from typing import Type

from steamship.invocable import Config, InvocableResponse, create_handler
from steamship.invocable.plugin_service import PluginRequest
from steamship.plugin.file_importer import FileImporter
from steamship.plugin.inputs.file_import_plugin_input import FileImportPluginInput
from steamship.plugin.outputs.raw_data_plugin_output import RawDataPluginOutput


class TestFileImporterPythonErrorPlugin(FileImporter):
    class EmptyConfig(Config):
        pass

    def config_cls(self) -> Type[Config]:
        return self.EmptyConfig

    def run(
        self, request: PluginRequest[FileImportPluginInput]
    ) -> InvocableResponse[RawDataPluginOutput]:
        raise Exception("TestFileImporterPythonErrorPlugin")


handler = create_handler(TestFileImporterPythonErrorPlugin)
