from __future__ import annotations

from steamship.data.file import File
from steamship.plugin.outputs.plugin_output import PluginOutput


class BlockAndTagPluginOutput(PluginOutput):
    file: File = None
