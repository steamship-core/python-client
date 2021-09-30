from typing import List, Dict, Callable
from dataclasses import dataclass
from nludb.types.base import NludbRequest, NludbResponseData

@dataclass
class Token:
  text: str = None
  textWithWs: str = None
  whitespace: str = None
  head: str = None
  headI: int = None
  leftEdge: str = None
  rightEdge: str = None
  entType: str = None
  entIob: str = None
  lemma: str = None
  normalized: str = None
  shape: str = None
  prefix: str = None
  suffix: str = None
  isAlpha: bool = None
  isAscii: bool = None
  isDigit: bool = None
  isTitle: bool = None
  isPunct: bool = None
  isLeftPunct: bool = None
  isRightPunct: bool = None
  isSpace: bool = None
  isBracket: bool = None
  isQuote: bool = None
  isCurrency: bool = None
  likeUrl: bool = None
  likeNum: bool = None
  likeEmail: bool = None
  isOov: bool = None
  isStop: bool = None
  pos: str = None
  tag: str = None
  dep: str = None
  lang: str = None
  prob: float = None
  charIndex: int = None
  tokenIndex: int = None

  @staticmethod
  def safely_from_dict(d: any) -> "Token":
    return Token(
      text = d.get("text", None),
      textWithWs = d.get("textWithWs", None),
      whitespace = d.get("whitespace", None),
      head = d.get("head", None),
      headI = d.get("headI", None),
      leftEdge = d.get("leftEdge", None),
      rightEdge = d.get("rightEdge", None),
      entType = d.get("entType", None),
      entIob = d.get("entIob", None),
      lemma = d.get("lemma", None),
      normalized = d.get("normalized", None),
      shape = d.get("shape", None),
      prefix = d.get("prefix", None),
      suffix = d.get("suffix", None),
      isAlpha = d.get("isAlpha", None),
      isAscii = d.get("isAscii", None),
      isDigit = d.get("isDigit", None),
      isTitle = d.get("isTitle", None),
      isPunct = d.get("isPunct", None),
      isLeftPunct = d.get("isLeftPunct", None),
      isRightPunct = d.get("isRightPunct", None),
      isSpace = d.get("isSpace", None),
      isBracket = d.get("isBracket", None),
      isQuote = d.get("isQuote", None),
      isCurrency = d.get("isCurrency", None),
      likeUrl = d.get("likeUrl", None),
      likeNum = d.get("likeNum", None),
      likeEmail = d.get("likeEmail", None),
      isOov = d.get("isOov", None),
      isStop = d.get("isStop", None),
      pos = d.get("pos", None),
      tag = d.get("tag", None),
      dep = d.get("dep", None),
      lang = d.get("lang", None),
      prob = d.get("prob", None),
      charIndex = d.get("charIndex", None),
      tokenIndex = d.get("tokenIndex", None)
    )

  @staticmethod
  def from_spacy(t: any, includeParseData: bool=True) -> "Token":
    if includeParseData is False:
      return Token(
        text = t.text,
        textWithWs = t.text_with_ws,
        whitespace = t.whitespace_,
        leftEdge = t.left_edge.text,
        rightEdge = t.right_edge.text,
        lemma = t.lemma_,
        isOov = t.is_oov,
        isStop = t.is_stop,
        charIndex = t.idx,
        tokenIndex = t.i,
      )

    return Token(
      text = t.text,
      textWithWs = t.text_with_ws,
      whitespace = t.whitespace_,
      head = t.head.text,
      headI = t.head.i,
      leftEdge = t.left_edge.text,
      rightEdge = t.right_edge.text,
      entType = t.ent_type_,
      entIob = t.ent_iob_,
      lemma = t.lemma_,
      normalized = t.norm_,
      shape = t.shape_,
      prefix = t.prefix_,
      suffix = t.suffix_,
      isAlpha = t.is_alpha,
      isAscii = t.is_ascii,
      isDigit = t.is_digit,
      isTitle = t.is_title,
      isPunct = t.is_punct,
      isLeftPunct = t.is_left_punct,
      isRightPunct = t.is_right_punct,
      isSpace = t.is_space,
      isBracket = t.is_bracket,
      isQuote = t.is_quote,
      isCurrency = t.is_currency,
      likeUrl = t.like_url,
      likeNum = t.like_num,
      likeEmail = t.like_email,
      isOov = t.is_oov,
      isStop = t.is_stop,
      pos = t.pos_,
      tag = t.tag_,
      dep = t.dep_.upper(),
      lang = t.lang_,
      prob = t.prob,
      charIndex = t.idx,
      tokenIndex = t.i,
    )

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
  def safely_from_dict(d: any) -> "Entity":
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

  @staticmethod
  def safely_from_dict(d: any) -> "Span":
    return Span(
      text = d.get("text", None),
      textWithWs = d.get("textWithWs", None),
      startChar = d.get("startChar", None),
      endChar = d.get("endChar", None),
      startToken = d.get("startToken", None),
      endToken = d.get("endToken", None),
      label = d.get("label", None),
      lemma = d.get("lemma", None),
      sentiment = d.get("sentiment", None)
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
  sentiment: float

  @staticmethod
  def safely_from_dict(d: any) -> "Sentence":
    tokens = [Token.safely_from_dict(h) for h in (d.get("tokens", []) or [])]
    entities = [Entity.safely_from_dict(h) for h in (d.get("entities", []) or [])]
    spans = [Span.safely_from_dict(h) for h in (d.get("spans", []) or [])]

    return Sentence(
      text=d.get("text", None),
      tokens=tokens,
      entities=entities,
      spans=spans,
      sentiment = d.get("sentiment", None)
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

@dataclass
class Doc:
  text: str
  sentences: List[Sentence]
  spans: List[Span]
  model: str
  lang: str
  sentiment: float
  entities: List[Entity]

  @staticmethod
  def safely_from_dict(d: any) -> "Doc":
    sentences = [Sentence.safely_from_dict(h) for h in (d.get("sentences", []) or [])]
    spans = [Span.safely_from_dict(h) for h in (d.get("spans", []) or [])]
    entities = [Entity.safely_from_dict(h) for h in (d.get("entities", []) or [])]

    return Doc(
      text=d.get("text", None),
      sentences=sentences,
      spans=spans,
      model=d.get("model", None),
      lang=d.get("lang", None),
      sentiment = d.get("sentiment", None),
      entities = entities
    )

  @staticmethod
  def from_spacy(
    text: str, 
    model: str, 
    d: any, 
    includeTokens: bool=True, 
    includeParseData: bool=True, 
    includeEntities: bool=True, 
    sentenceFilterFn: Callable[[any], bool]=None
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
      text=text,
      sentences=sentences,
      spans=spans,
      model=model,
      lang=d.lang_,
      sentiment=d.sentiment,
      entities=entities
    )
    return ret
  
@dataclass
class ParseResponse(NludbResponseData):
  docs: List[Doc] = None

  @staticmethod
  def safely_from_dict(d: any) -> "ParseResponse":
    docs = [Doc.safely_from_dict(h) for h in (d.get("docs", []) or [])]
    return ParseResponse(
      docs=docs
    )

MatcherClause = Dict[str, any]
Matcher = List[MatcherClause]

@dataclass
class TokenMatcher():
  label: str = None
  patterns: List[Matcher] = None

  @staticmethod
  def safely_from_dict(d: any) -> "TokenMatcher":
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
  def safely_from_dict(d: any) -> "PhraseMatcher":
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
  def safely_from_dict(d: any) -> "DependencyMatcher":
    return DependencyMatcher(
      label=d.get("label", None),
      patterns=(d.get("patterns", []) or [])
    )

@dataclass
class ParseRequest(NludbResponseData):
  docs: List[str] = None
  model: str = None
  tokenMatchers: List[TokenMatcher] = None
  phraseMatchers: List[PhraseMatcher] = None
  dependencyMatchers: List[DependencyMatcher] = None

  includeTokens: bool = True
  includeParseData: bool = True
  includeEntities: bool = False

  metadata: any = None

  @staticmethod
  def safely_from_dict(d: any) -> "ParseRequest":
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
      model=d.get("model", None),
      tokenMatchers=token_matchers,
      phraseMatchers=phrase_matchers,
      dependencyMatchers=dependency_matchers,
      includeTokens=includeTokens,
      includeParseData=includeParseData,
      includeEntities=includeEntities,
      metadata=metadata
    )

