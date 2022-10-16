from typing import Optional


class TagKind:
    """A set of `kind` constants for Tags."""

    pos = "pos"  # Part of speech tags
    dep = "dep"  # Dependency tags
    sentiment = "sentiment"  # Sentiment tags
    emotion = "emotion"  # Emotion tags
    ent = "ent"  # Entity tags, such as PERSON or ORG
    doc = "doc"  # Doc-level semantics, such as H1, P, S. See `DocTag` for `name` constants
    token = "token"  # Token-level semantics, such as isQuote. See Token for `name` constants. # noqa: S105
    embedding = "embedding"  # A vector representation of text


class DocTag:
    """A set of `name` constants for for Tags with a `kind` of `TagKind.doc`; appropriate for HTML and Markdown ideas."""

    doc = "doc"
    page = "page"  # E.g. in a PDF
    region = "region"  # E.g., abstract catchall region in a document
    header = "header"
    h1 = "h1"
    h2 = "h2"
    h3 = "h3"
    h4 = "h4"
    h5 = "h5"
    line = "line"
    title = "title"
    subtitle = "subtitle"
    footer = "footer"
    paragraph = "paragraph"
    list = "list"
    list_item = "listitem"
    link = "link"
    caption = "caption"
    image = "image"
    blockquote = "blockquote"
    blockcode = "blockcode"
    unk = "unk"
    sentence = "sentence"
    token = "token"  # noqa: S105
    span = "span"
    div = "div"
    pre = "pre"
    strong = "strong"
    emph = "emph"
    underline = "underline"
    teletype = "teletype"

    @staticmethod
    def from_html_tag(tagname: Optional[str]) -> Optional[str]:  # noqa: C901
        if tagname is None:
            return None

        name = tagname.lower().strip()

        if name == "p":
            return DocTag.paragraph
        elif name == "h1":
            return DocTag.h1
        elif name == "h2":
            return DocTag.h2
        elif name == "h3":
            return DocTag.h3
        elif name == "h4":
            return DocTag.h4
        elif name == "h5":
            return DocTag.h5
        elif name == "ul":
            return DocTag.list
        elif name == "li":
            return DocTag.list_item
        elif name == "a":
            return DocTag.link
        elif name == "div":
            return DocTag.div
        elif name == "img":
            return DocTag.image
        elif name == "span":
            return DocTag.span
        elif name == "pre":
            return DocTag.pre
        elif name == "code":
            return DocTag.blockcode
        elif name == "blockquote":
            return DocTag.blockquote
        elif name == "strong":
            return DocTag.strong
        elif name == "b":
            return DocTag.strong
        elif name == "emph":
            return DocTag.emph
        elif name == "i":
            return DocTag.emph
        elif name == "u":
            return DocTag.underline
        elif name == "tt":
            return DocTag.teletype

        return None


class TokenTag:
    """A set of `name` constants for Tags with a `kind` of `TagKind.token`; appropriate for parsing-level ideas."""

    TextWithWs = "textWithWs"
    Whitespace = "whitespace"
    Head = "head"
    LeftEdge = "leftEdge"
    RightEdge = "rightEdge"
    EntType = "entType"
    EntIob = "entIob"
    Lemma = "lemma"
    Normalized = "normalized"
    Shape = "shape"
    Prefix = "prefix"
    Suffix = "suffix"
    IsAlpha = "isAlpha"
    IsAscii = "isAscii"
    IsDigit = "isDigit"
    IsTitle = "isTitle"
    IsPunct = "isPunct"
    IsLeftPunct = "isLeftPunct"
    IsRightPunct = "isRightPunct"
    IsSpace = "isSpace"
    IsBracket = "isBracket"
    IsQuote = "isQuote"
    IsCurrency = "isCurrency"
    LikeUrl = "likeUrl"
    LikeNum = "likeNum"
    LikeEmail = "likeEmail"
    IsOov = "isOov"
    IsStop = "isStop"
    Lang = "lang"


class SentimentTag:
    """A set of `name` constants for Tags with a `kind` of `TagKind.sentiment`."""

    positive = "positive"
    neutral = "neutral"
    negative = "negative"
    score = "score"


class EmotionTag:
    """A set of `name` constants for Tags with a `kind` of `TagKind.emotion`."""

    positive = "positive"
    neutral = "neutral"
    negative = "negative"
    happiness = "happiness"
    sadness = "sadness"
    joy = "joy"
    love = "love"
    anger = "anger"
    fear = "fear"
    surprise = "surprise"
    score = "score"


class TagValue:
    """A set of key constants for the `value` object within a tag.."""

    score = "score"
    value = "value"
