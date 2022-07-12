"""CSV Blockifier - Steamship Plugin."""

from logging import Logger
from typing import Any, Dict

from steamship.app import create_handler
from steamship.plugin.blockifier import Blockifier
from tests.assets.plugins.blockifiers.csv_blockifier import CsvBlockifier


class TsvBlockifier(CsvBlockifier, Blockifier):
    """Converts TSV into Tagged Steamship Blocks.

    Implementation is only here to demonstrate how plugins can be built through inheritance.
    """

    def __init__(self, client=None, config: Dict[str, Any] = None, logger: Logger = None):
        super().__init__(client, config, logger)
        self.config.delimiter = "\t"


handler = create_handler(TsvBlockifier)
