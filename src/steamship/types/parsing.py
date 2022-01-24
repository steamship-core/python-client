from dataclasses import dataclass
from typing import List, Dict, Callable
from steamship.types.base import Request, Model
from steamship.client.base import ApiBase
from steamship.types.block import Block
from steamship.types.token import Token
import json

@dataclass
class Entity:
  text: str
  textWithWs: str
  startChar: int
  endChar: int
  startToken: int
  endToken: int
  label: str
  lemma: str

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "Entity":
    return Entity(
      text = d.get("text", None),
      textWithWs = d.get("textWithWs", None),
      startChar = d.get("startChar", None),
      endChar = d.get("endChar", None),
      startToken = d.get("startToken", None),
      endToken = d.get("endToken", None),
      label = d.get("label", None),
      lemma = d.get("lemma", None)
    )

  @staticmethod
  def from_spacy(ent: any) -> "Entity":
    return Entity(
      text=ent.text,
      textWithWs=ent.text_with_ws,
      startChar=ent.start_char,
      endChar=ent.end_char,
      startToken=ent.start,
      endToken=ent.end,
      label=ent.label_,
      lemma=ent.lemma_,
    )

@dataclass
class Span:
  text: str
  textWithWs: str
  startChar: int
  endChar: int
  startToken: int
  endToken: int
  label: str
  lemma: str
  sentiment: float
  score: float

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "Span":
    return Span(
      text = d.get("text", None),
      textWithWs = d.get("textWithWs", None),
      startChar = d.get("startChar", None),
      endChar = d.get("endChar", None),
      startToken = d.get("startToken", None),
      endToken = d.get("endToken", None),
      label = d.get("label", None),
      lemma = d.get("lemma", None),
      sentiment = d.get("sentiment", None),
      score = d.get("score", None),
    )

  @staticmethod
  def from_spacy(ent: any) -> "Span":
    return Span(
      text=ent.text,
      textWithWs=ent.text_with_ws,
      startChar=ent.start_char,
      endChar=ent.end_char,
      startToken=ent.start,
      endToken=ent.end,
      label=ent.label_,
      lemma=ent.lemma_,
      sentiment=ent.sentiment
    )

@dataclass
class Sentence:
  text: str
  tokens: List[Token]
  entities: List[Entity]
  spans: List[Span]
  sentiment: float = None
  blockId: str = None

  def tokens_for_char_span(self, startCharIndex: int, endCharIndex: int) -> List[Token]:
    ret = []
    if self.tokens:
      for token in sorted(self.tokens, key=lambda t: t.charIndex):
        endIndex = token.charIndex + len(token.text)
        if token.charIndex >= startCharIndex and endIndex <= endCharIndex:
          ret.append(token)
    return ret

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "Sentence":
    tokens = [Token.safely_from_dict(h) for h in (d.get("tokens", []) or [])]
    entities = [Entity.safely_from_dict(h) for h in (d.get("entities", []) or [])]
    spans = [Span.safely_from_dict(h) for h in (d.get("spans", []) or [])]

    return Sentence(
      text=d.get("text", None),
      tokens=tokens,
      entities=entities,
      spans=spans,
      sentiment = d.get("sentiment", None),
      blockId=d.get('blockId', None)
    )

  @staticmethod
  def from_spacy(d: any, includeTokens: bool=True, includeParseData: bool=True, includeEntities: bool=True) -> "Sentence":
    tokens = [Token.from_spacy(t, includeParseData=includeParseData) for t in d] if includeTokens is True else []
    entities = [Entity.from_spacy(e) for e in d.ents] if includeEntities is True else []

    return Sentence(
      text=d.text,
      tokens=tokens,
      entities=entities,
      spans=[],
      sentiment=d.sentiment
    )

  def __iter__(self):
    if self.tokens is None:
      return None
    return self.tokens.__iter__
  
  def __getitem__(self, index):
    if self.tokens is None:
      return None
    return self.tokens.__getitem__(index)

  def __next__(self):
    if self.tokens is None:
      return None
    return self.tokens.__next__()

@dataclass
class Doc:
  text: str
  id: str
  children: List[Sentence]
  spans: List[Span]
  model: str
  lang: str
  sentiment: float
  entities: List[Entity]
  blockId: str = None

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "Doc":
    sentences = [Sentence.safely_from_dict(h) for h in (d.get("sentences", []) or [])]
    spans = [Span.safely_from_dict(h) for h in (d.get("spans", []) or [])]
    entities = [Entity.safely_from_dict(h) for h in (d.get("entities", []) or [])]

    return Doc(
      id=d.get("id", None),
      text=d.get("text", None),
      children=sentences,
      spans=spans,
      model=d.get("model", None),
      lang=d.get("lang", None),
      sentiment = d.get("sentiment", None),
      entities = entities,
      blockId=d.get('blockId', None)
    )

  @staticmethod
  def from_spacy(
    text: str, 
    model: str, 
    d: any, 
    includeTokens: bool=True, 
    includeParseData: bool=True, 
    includeEntities: bool=True, 
    sentenceFilterFn: Callable[[any], bool]=None,
    id: str=None
    ) -> "Doc":
    sentences = [
      Sentence.from_spacy(s, includeTokens=includeTokens, includeParseData=includeParseData, includeEntities=includeEntities) 
      for s in d.sents
      if sentenceFilterFn is None or sentenceFilterFn(s) is True
    ]
    spans = []
    for label in d.spans:
      span_group = d.spans[label]
      for s in span_group:
        spans.append(Span.safely_from_dict(s))

    entities = []
    if includeEntities is True:
      for ent in d.ents:
        e = Entity.from_spacy(ent)
        if e is not None:
          entities.append(e)

    ret = Doc(
      id=id,
      text=text,
      children=sentences,
      spans=spans,
      model=model,
      lang=d.lang_,
      sentiment=d.sentiment,
      entities=entities
    )
    return ret

  
@dataclass
class ParseResponse(Model):
  client: ApiBase = None
  blocks: List[Block] = None

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "ParseResponse":
    blocks = [Block.safely_from_dict(h, client) for h in (d.get("blocks", []) or [])]
    return ParseResponse(
      client=client,
      blocks=blocks
    )

MatcherClause = Dict[str, any]
Matcher = List[MatcherClause]

@dataclass
class TokenMatcher():
  label: str = None
  patterns: List[Matcher] = None

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "TokenMatcher":
    return TokenMatcher(
      label=d.get("label", None),
      patterns=(d.get("patterns", []) or [])
    )

@dataclass
class PhraseMatcher():
  label: str = None
  phrases: List[str] = None
  attr: str = None

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "PhraseMatcher":
    return PhraseMatcher(
      label=d.get("label", None),
      phrases=(d.get("phrases", []) or []),
      attr=d.get("attr", None)
    )

@dataclass
class DependencyMatcher():
  label: str = None
  # Note: Add a LABEL field to the matcher clause to have a token
  # get labeled in the response.
  patterns: List[Matcher] = None

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "DependencyMatcher":
    return DependencyMatcher(
      label=d.get("label", None),
      patterns=(d.get("patterns", []) or [])
    )

@dataclass
class ParseRequest(Request):
  type: str = None
  id: str = None
  name: str = None
  handle: str = None
  docs: List[str] = None
  blockIds: List[str] = None

  model: str = None
  tokenMatchers: List[TokenMatcher] = None
  phraseMatchers: List[PhraseMatcher] = None
  dependencyMatchers: List[DependencyMatcher] = None

  includeTokens: bool = True
  includeParseData: bool = True
  includeEntities: bool = False

  metadata: any = None

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "ParseRequest":
    token_matchers = [TokenMatcher.safely_from_dict(h) for h in (d.get("tokenMatchers", []) or [])]
    phrase_matchers = [PhraseMatcher.safely_from_dict(h) for h in (d.get("phraseMatchers", []) or [])]
    dependency_matchers = [DependencyMatcher.safely_from_dict(h) for h in (d.get("dependencyMatchers", []) or [])]

    includeTokens = d.get("includeTokens", True)
    if includeTokens is None:
      includeTokens = True

    includeParseData = d.get("includeParseData", True)
    if includeParseData is None:
      includeParseData = True

    includeEntities = d.get("includeEntities", True)
    if includeEntities is None:
      includeEntities = True

    metadata = d.get("metadata", None)
    if metadata is not None:
      try:
        metadata = json.loads(metadata)
      except:
        pass

    return ParseRequest(
      docs=(d.get("docs", []) or []),
      blockIds=(d.get("blockIds", []) or []),
      model=d.get("model", None),
      tokenMatchers=token_matchers,
      phraseMatchers=phrase_matchers,
      dependencyMatchers=dependency_matchers,
      includeTokens=includeTokens,
      includeParseData=includeParseData,
      includeEntities=includeEntities,
      metadata=metadata
    )



# @dataclass
# class ParseRequest(Request):
#   type: str
#   model: str = None
#   id: str = None
#   handle: str = None
#   name: str = None
#   tokenMatchers: List[TokenMatcher] = None
#   phraseMatchers: List[PhraseMatcher] = None
#   dependencyMatchers: List[DependencyMatcher] = None

# @dataclass
# class ParseResponse(Model):
#   fileId: str

#   @staticmethod
#   def safely_from_dict(d: any, client: ApiBase = None) -> "ParseResponse":
#     return ParseResponse(
#       fileId = d.get('fileId', None)
#     )