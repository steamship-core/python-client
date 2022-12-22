"""CSV Blockifier - Steamship Plugin."""

from typing import Any, Dict

from assets.plugins.blockifiers.csv_blockifier import CsvBlockifier

from steamship.invocable import InvocationContext, create_handler
from steamship.plugin.blockifier.blockifier import Blockifier


class TsvBlockifier(CsvBlockifier, Blockifier):
    """Converts TSV into Tagged Steamship Blocks.

    Implementation is only here to demonstrate how plugins can be built through inheritance.
    """

    def __init__(
        self, client=None, config: Dict[str, Any] = None, context: InvocationContext = None
    ):
        super().__init__(client, config, context)
        self.config.delimiter = "\t"


handler = create_handler(TsvBlockifier)
