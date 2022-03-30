from steamship import Block, BlockTypes, Token
from steamship.app import App, post, create_handler
from steamship.plugin.parser import Parser, ParseResponse, ParseRequest
from steamship.plugin.service import PluginResponse, PluginRequest


def _makeSentenceBlock(sentence: str, includeTokens: bool = True) -> Block:
    """Splits the sentence in tokens on space. Dep head of all is first token"""
    if includeTokens:
        tokens = [Token(text=word, parentIndex=0) for word in sentence.split(" ")]
        return Block(type=BlockTypes.Sentence, text=sentence, tokens=tokens)
    else:
        return Block(type=BlockTypes.Sentence, text=sentence)


def _makeDocBlock(text: str, blockId: str = None, includeTokens=True) -> Block:
    """Splits the document into sentences by assuming a period is a sentence divider."""
    # Add the period back
    sentences = list(map(lambda s: "{}.".format(s), text.split(".")))
    children = [_makeSentenceBlock(sentence, includeTokens=includeTokens) for sentence in sentences]
    return Block(id=blockId, text=text, type=BlockTypes.Document, children=children)


def _makeTestResponse(request: ParseRequest) -> ParseResponse:
    blocks = []
    for i, doc in enumerate(request.docs):
        # This is awkward and we shouldn're require plugin authors to return
        # the block ID below if possible... (Note: it's necessary for knowing
        # where in the DB to fold the results back into.)
        blockId = None
        if request.blockIds is not None and i < len(request.blockIds):
            i = request.blockIds[i]
        blocks.append(
            _makeDocBlock(
                doc,
                blockId=blockId,
                includeTokens=request.includeTokens is None or request.includeTokens is True
            )
        )
    response = ParseResponse(blocks=blocks)
    return response


class TestParserPlugin(Parser, App):
    # TODO: WARNING! We will need to implement some logic that prevents 
    # a distributed endless loop. E.g., a parser plugin returning the results
    # of using the Steamship client to call parse.. via itself!

    def run(self, request: PluginRequest[ParseRequest]) -> PluginResponse[ParseResponse]:
        if request.data is not None:
            return PluginResponse(
                data=_makeTestResponse(request.data)
            )

    @post('tag')
    def parse(self, **kwargs) -> dict:
        parseRequest = Parser.parse_request(request=kwargs)
        parseResponse = self.run(parseRequest)
        return Parser.response_to_dict(parseResponse)


handler = create_handler(TestParserPlugin)
