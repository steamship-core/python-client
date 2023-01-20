from typing import List

from steamship import Block, File, Tag
from steamship.data import TagKind, TagValueKey
from steamship.invocable import InvocableResponse, create_handler
from steamship.invocable.plugin_service import PluginRequest
from steamship.plugin.embedder import Embedder
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput

FEATURES = [
    "employee",
    "roses",
    "run",
    "bike",
    "ted",
    "grace",
    "violets",
    "sugar",
    "sweet",
    "cake",
    "flour",
    "chocolate",
    "vanilla",
    "flavors",
    "flavor",
    "can",
    "armadillo",
    "pizza",
    "ship",
    "run",
    "jerry",
    "ronaldo",
    "ted",
    "brenda",
    "susan",
    "sam",
    "jerry",
    "shoe",
    "cheese",
    "water",
    "drink",
    "glass",
    "egg",
    "sleep",
    "code",
    "jonathan",
    "dolphin",
    "apple",
    "orange",
    "number",
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
    "16",
    "17",
    "bad",
    "terrible",
    "average",
    "good",
]

DIMENSIONALITY = len(FEATURES)


def embed(s: str) -> List[float]:
    s = s.lower()
    return list(map(lambda word: 1.0 if word in s else 0.0, FEATURES))


def _embed_to_tag(s: str) -> Tag:
    embedding = embed(s)
    return Tag(
        kind=TagKind.EMBEDDING, name="my-embedding", value={TagValueKey.VECTOR_VALUE: embedding}
    )


def _embed_block(block: Block) -> Block:
    return Block(id=block.id, text=block.text, tags=[_embed_to_tag(block.text)])


class TestEmbedderPlugin(Embedder):
    def run(
        self, request: PluginRequest[BlockAndTagPluginInput]
    ) -> InvocableResponse[BlockAndTagPluginOutput]:
        updated_blocks = [_embed_block(block) for block in request.data.file.blocks]
        return InvocableResponse(data=BlockAndTagPluginOutput(file=File(blocks=updated_blocks)))


handler = create_handler(TestEmbedderPlugin)
