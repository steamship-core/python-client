from typing import List

from steamship.app import App, post, create_handler, Response
from steamship.plugin.embedder import Embedder
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.outputs.embedded_items_plugin_output import EmbeddedItemsPluginOutput
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


class TestEmbedderPlugin(Embedder, App):
    def run(self, request: PluginRequest[BlockAndTagPluginInput]) -> PluginResponse[EmbeddedItemsPluginOutput]:
        embeddings = list(map(lambda s: embed(s.text), request.data.file.blocks))
        return PluginResponse(data=EmbeddedItemsPluginOutput(embeddings=embeddings))

    @post('embed')
    def embed(self, **kwargs) -> Response:
        embedRequest = Embedder.parse_request(request=kwargs)
        objResponse = self.run(embedRequest)
        dictResponse = Embedder.response_to_dict(objResponse)
        response = Response(json=dictResponse)
        return response


handler = create_handler(TestEmbedderPlugin)
