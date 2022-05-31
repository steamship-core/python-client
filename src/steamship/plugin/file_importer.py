from abc import ABC, abstractmethod

from steamship.app import Response, post
from steamship.plugin.inputs.file_import_plugin_input import FileImportPluginInput
from steamship.plugin.outputs.raw_data_plugin_output import RawDataPluginOutput
from steamship.plugin.service import PluginRequest, PluginService


# Note!
# =====
#
# This is the PLUGIN IMPLEMENTOR's View of a File Importer.
#
# If you are using the Steamship Client, you probably want steamship.client.operations.file_importer instead
# of this file.
#
class FileImporter(PluginService[FileImportPluginInput, RawDataPluginOutput], ABC):
    @abstractmethod
    def run(self, request: PluginRequest[FileImportPluginInput]) -> Response[RawDataPluginOutput]:
        raise NotImplementedError()

    @post("import")
    def run_endpoint(self, **kwargs) -> Response[RawDataPluginOutput]:
        """Exposes the File Importer's `run` operation to the Steamship Engine via the expected HTTP path POST /import"""
        return self.run(PluginRequest[FileImportPluginInput](**kwargs))
