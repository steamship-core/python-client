from abc import ABC

from steamship.base import Client
from steamship.plugin.inputs.file_import_plugin_input import FileImportPluginInput
from steamship.plugin.outputs.raw_data_plugin_output import RawDataPluginOutput
from steamship.plugin.service import PluginService, PluginRequest

# Note!
# =====
#
# This is the PLUGIN IMPLEMENTOR's View of a File Importer.
#
# If you are using the Steamship Client, you probably want steamship.client.operations.file_importer instead
# of this file.
#
class FileImporter(PluginService[FileImportPluginInput, RawDataPluginOutput], ABC):
    @classmethod
    def subclass_request_from_dict(cls, d: any, client: Client = None) -> PluginRequest[FileImportPluginInput]:
        return FileImportPluginInput.from_dict(d, client=client)
