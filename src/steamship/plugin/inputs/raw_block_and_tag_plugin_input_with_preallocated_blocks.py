from typing import List

from steamship import Block
from steamship.plugin.inputs.raw_block_and_tag_plugin_input import RawBlockAndTagPluginInput


class RawBlockAndTagPluginInputWithPreallocatedBlocks(RawBlockAndTagPluginInput):
    output_blocks: List[Block]
