from dataclasses import dataclass
from typing import List

from steamship.base.client import ApiBase
from steamship.base.response import Model
from steamship.types.span import Span
from steamship.types.token import Token


class BlockTypes:
    Document = "doc"
    Page = "page"  # E.g. in a PDF
    Region = "region"  # E.g., abstract catchall region in a document
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
    spans: List["Span"] = None

    @staticmethod
    def from_dict(d: any, client: ApiBase) -> "Block":
        if d is None:
            return None
        if 'block' in d:
            d = d['block']
        return Block(
            client=client,
            id=d.get('id', None),
            type=d.get('type', None),
            text=d.get('text', None),
            children=list(map(lambda child: Block.from_dict(child, client), d.get('children', []))),
            tokens=list(map(lambda token: Token.from_dict(token, client), d.get('tokens', []))),
            # spans = list(map(lambda span: Span.from_dict(span, client), d.get('span', []))),
        )

    @staticmethod
    def from_spacy_root(
            id: str = None,
            spacyObj: any = None,
            includeTokens: bool = True,
            includeParseData: bool = True,
            includeEntities: bool = True
    ) -> "Block":
        children = None
        if spacyObj is not None:
            children = [
                Block.from_spacy(
                    type=BlockTypes.Sentence,
                    spacyObj=spacySent,
                    includeTokens=includeTokens,
                    includeParseData=includeParseData,
                    includeEntities=includeEntities
                )
                for spacySent in spacyObj.sents
            ]

        # spans = []
        # for label in d.spans:
        #   span_group = d.spans[label]
        #   for s in span_group:
        #     spans.append(Span.from_dict(s))

        # entities = []
        # if includeEntities is True:
        #   for ent in d.ents:
        #     e = Entity.from_spacy(ent)
        #     if e is not None:
        #       entities.append(e)

        return Block(
            id=id,
            type=BlockTypes.Document,
            children=children
        )

    @staticmethod
    def from_spacy(
            spacyObj: any = None,
            type: any = None,
            includeTokens: bool = True,
            includeParseData: bool = True,
            includeEntities: bool = True
    ) -> "Block":

        if spacyObj is None:
            return None

        tokens = [
            Token.from_spacy(
                token,
                includeParseData=includeParseData
            ) for token in spacyObj] if includeTokens is True else []

        # entities = [Entity.from_spacy(e) for e in d.ents] if includeEntities is True else []

        return Block(
            type=type,
            text=spacyObj.text,
            tokens=tokens,
            spans=[]
        )

    def to_dict(self) -> dict:
        children = None
        if self.children is not None:
            children = [child.to_dict() for child in self.children]

        tokens = None
        if self.tokens is not None:
            tokens = [token.to_dict() for token in self.tokens]

        spans = None
        if self.spans is not None:
            spans = [span.to_dict() for span in self.spans]

        return dict(
            id=self.id,
            type=self.type,
            text=self.text,
            children=children,
            tokens=tokens,
            spans=spans
        )
