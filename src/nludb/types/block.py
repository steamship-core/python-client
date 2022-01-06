from dataclasses import dataclass
from nludb.api.base import ApiBase
from nludb.types.base import Response
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
class Block(Response):
  client: ApiBase = None
  id: str = None
  type: str = None
  value: str = None
  children: List["Block"] = None

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase) -> "Block":
    return Block(
      client = client,
      id = d.get('id', None),
      type = d.get('type', None),
      value = d.get('value', None),
      children = map(lambda child: Block.safely_from_dict(child, client), d.get('children', []))
    )