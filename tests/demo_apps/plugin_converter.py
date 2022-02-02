from steamship.plugin.service import PluginResponse, PluginRequest
from steamship.plugin.converter import Converter, ConvertResponse, ConvertRequest
from steamship.app import App, post, create_lambda_handler
from .plugin_importer import TEST_H1, TEST_S1, TEST_S2, TEST_S3
from steamship import Block, BlockTypes

class TestConverterPlugin(Converter, App):
    def run(self, request: PluginRequest[ConvertRequest]) -> PluginResponse[ConvertResponse]:
        return PluginResponse(data=ConvertResponse(root=Block(
            type=BlockTypes.Document,
            children=[
                Block(text=TEST_H1, type = BlockTypes.H1),
                Block(type = BlockTypes.Paragraph, children=[
                    Block(text=TEST_S1, type = BlockTypes.Sentence),
                    Block(text=TEST_S2, type = BlockTypes.Sentence)
                ]),
                Block(type=BlockTypes.Paragraph, text=TEST_S3)
            ]
        )))

    @post('do_import')
    def do_import(self, request: dict) -> dict:
        convertRequest = self.__class__.parse_request(request)
        convertResponse = self.run(convertRequest)
        return self.__class__.response_to_dict(convertResponse)

handler = create_lambda_handler(TestConverterPlugin)
