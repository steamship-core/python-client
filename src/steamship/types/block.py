from dataclasses import dataclass
from steamship.client.base import ApiBase
from steamship.types.base import Model
from steamship.types.token import Token
from typing import List

class BlockTypes:
  Document = "doc"
  Page = "page" # E.g. in a PDF
  Region = "region" # E.g., abstract catchall region in a document
  Header = "header"
  H1 = "h1"
  H2 = "h2"
  H3 = "h3"
  H4 = "h4"
  H5 = "h5"
  Line = "line"
  Title = "title"
  Subtitle = "subtitle"
  Footer = "footer"
  Paragraph = "paragraph"
  List = "list"
  Blockquote = "blockquote"
  Blockcode = "blockcode"
  Unk = "unk"
  Sentence = "sentence"
  Token = "token"
  Span = "span"

@dataclass
class Block(Model):
  client: ApiBase = None
  id: str = None
  type: str = None
  text: str = None
  children: List["Block"] = None
  tokens: List["Token"] = None

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase) -> "Block":
    if d is None:
      return None
    return Block(
      client = client,
      id = d.get('id', None),
      type = d.get('type', None),
      text = d.get('text', None),
      children = list(map(lambda child: Block.safely_from_dict(child, client), d.get('children', []))),
      tokens = list(map(lambda token: Token.safely_from_dict(token, client), d.get('tokens', [])))
    )