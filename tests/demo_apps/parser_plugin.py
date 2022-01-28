from typing import Dict
from steamship.server import post, App, post, create_lambda_handler
from steamship.types.parsing import ParseRequest, ParseResponse
from steamship.types.block import Block, BlockTypes
from steamship.types.token import Token
class TestParserPlugin(App):
    # TODO: WARNING! We will need to implement some logic that prevents 
    # a distributed endless loop. E.g., a parser plugin returning the results
    # of using the Steamship client to call parse.. via itself!

  def _makeSentenceBlock(self, sentence: str, includeTokens: bool = True) -> Block:
    """Splits the sentence in tokens on space. Dep head of all is first token"""
    if includeTokens:
      tokens = [Token(text=word, parentIndex=0) for word in sentence.split(" ")]
      return Block(type=BlockTypes.Sentence, text=sentence, tokens=tokens)
    else:
      return Block(type=BlockTypes.Sentence, text=sentence)

  def _makeDocBlock(self, text: str, blockId: str = None, includeTokens=True) -> Block:
    """Splits the document into sentences by assuming a period is a sentence divider."""
    # Add the period back
    sentences = list(map(lambda s: "{}.".format(s), text.split(".")))
    children = [self._makeSentenceBlock(sentence, includeTokens=includeTokens) for sentence in sentences]
    return Block(id=blockId, text=text, type=BlockTypes.Document, children=children)

  @post('parse')
  def parse(self, request: dict) -> dict:
    req = ParseRequest.safely_from_dict(request)
    blocks = []

    for i, doc in enumerate(request.docs):
      # This is awkward and we shouldn're require plugin authors to return
      # the block ID below if possible... (Note: it's necessary for knowing
      # where in the DB to fold the results back into.)
      blockId = None
      if request.blockIds is not None and i < request.blockIds:
        i = request.blockIds[i]
      blocks.append(
        self._makeDocBlock(
          doc, 
          blockId=blockId, 
          includeTokens=req.includeTokens is None or req.includeTokens is True
        )
      )
    
    response = ParseResponse(blocks=blocks)
    return response.safely_to_dict()


handler = create_lambda_handler(TestParserPlugin)
