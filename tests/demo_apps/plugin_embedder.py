from typing import List

from steamship import Tag, TagKind, TextTag, Block, File
from steamship.app import App, post, create_handler, Response
from steamship.plugin.embedder import Embedder
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.service import PluginResponse, PluginRequest

FEATURES = ["employee", "roses", "run", "bike", "ted", "grace", "violets", "sugar", "sweet", "cake",
            "flour", "chocolate", "vanilla", "flavors", "flavor", "can", "armadillo", "pizza",
            "ship", "run", "jerry", "ronaldo", "ted", "brenda", "susan", "sam", "jerry", "shoe",
            "cheese", "water", "drink", "glass", "egg", "sleep", "code", "jonathan", "dolphin", "apple",
            "orange", "number", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15",
            "16", "17", "bad", "terrible", "average", "good"]

DIMENSIONALITY = len(FEATURES)


def embed(s: str) -> List[float]:
    s = s.lower()
    return list(map(lambda word: 1.0 if word in s else 0.0, FEATURES))

def embedToTag(s: str) -> Tag.CreateRequest:
    embedding = embed(s)
    return Tag.CreateRequest(
        kind = TagKind.text,
        name =  TextTag.embedding,
        value = { TextTag.embedding : embedding }
    )

def embedBlock(block: Block) -> Block.CreateRequest:
    return Block.CreateRequest(
        id=block.id,
        text=block.text,
        tags=[embedToTag(block.text)]
    )


class TestEmbedderPlugin(Embedder, App):
    def run(self, request: PluginRequest[BlockAndTagPluginInput]) -> PluginResponse[BlockAndTagPluginOutput]:
        updatedBlocks = [ embedBlock(block) for block in request.data.file.blocks ]
        return PluginResponse(data=BlockAndTagPluginOutput(file=File.CreateRequest(blocks = updatedBlocks)))

    @post('tag')
    def embed(self, **kwargs) -> Response:
        embedRequest = Embedder.parse_request(request=kwargs)
        objResponse = self.run(embedRequest)
        dictResponse = Embedder.response_to_dict(objResponse)
        response = Response(json=dictResponse)
        return response


handler = create_handler(TestEmbedderPlugin)
