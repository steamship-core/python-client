from dataclasses import dataclass
from typing import Callable
from steamship.types.base import  Model
from steamship.client.base import ApiBase

@dataclass
class Token(Model):
  client: ApiBase = None
  id: str = None
  blockId: bool = None
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
  def from_dict(d: any, client: ApiBase = None) -> "Token":
    return Token(
      client = client,
      id = d.get("id", None),
      blockId = d.get("blockId", None),
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
      tokenIndex = d.get("tokenIndex", None),
    )

  def __len__(self):
    if self.text is None:
      return None
    return self.text.__len__

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
  
  def to_dict(self) -> dict:
    return dict(
      id=self.id,
      blockId=self.blockId,
      text=self.text,
      textWithWs=self.textWithWs,
      whitespace=self.whitespace,
      head=self.head,
      headI=self.headI,
      leftEdge=self.leftEdge,
      rightEdge=self.rightEdge,
      entType=self.entType,
      entIob=self.entIob,
      lemma=self.lemma,
      normalized=self.normalized,
      shape=self.shape,
      prefix=self.prefix,
      suffix=self.suffix,
      isAlpha=self.isAlpha,
      isAscii=self.isAscii,
      isDigit=self.isDigit,
      isTitle=self.isTitle,
      isPunct=self.isPunct,
      isLeftPunct=self.isLeftPunct,
      isRightPunct=self.isRightPunct,
      isSpace=self.isSpace,
      isBracket=self.isBracket,
      isQuote=self.isQuote,
      isCurrency=self.isCurrency,
      likeUrl=self.likeUrl,
      likeNum=self.likeNum,
      likeEmail=self.likeEmail,
      isOov=self.isOov,
      isStop=self.isStop,
      pos=self.pos,
      tag=self.tag,
      dep=self.dep,
      lang=self.lang,
      prob=self.prob,
      charIndex=self.charIndex,
      tokenIndex=self.tokenIndex
    )