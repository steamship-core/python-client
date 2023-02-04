from enum import Enum
from typing import Optional


class TagKind(str, Enum):
    """A set of `kind` constants for Tags.

    These define broad categories of tags. Suggested `name` values for each category are found in
    separate enums. For example: kind=TagKind.DOCUMENT, name=DocumentTag.H1
    """

    PART_OF_SPEECH = "part-of-speech"
    DEPENDENCY = "dependency"
    SENTIMENT = "sentiment"
    EMOTION = "emotion"
    ENTITY = "entity"
    DOCUMENT = "document"
    TOKEN = "token"  # noqa: S105
    INTENT = "intent"
    EMBEDDING = "embedding"
    GENERATION = "generation"
    PROVENANCE = "provenance"
    TOPIC = "topic"
    TOKENIZATION = "tokenization"
    KIND = "summary"
    TIMESTAMP = "timestamp"
    SUMMARY = "summary"
    SEARCH_RESULT = "search-result"


class DocTag(str, Enum):
    """A set of `name` constants for for Tags with a `kind` of `TagKind.doc`; appropriate for HTML and Markdown ideas."""

    DOCUMENT = "document"
    PAGE = "page"  # E.g. in a PDF
    REGION = "region"  # E.g., abstract catchall region in a document
    HEADER = "header"
    H1 = "h1"
    H2 = "h2"
    H3 = "h3"
    H4 = "h4"
    H5 = "h5"
    LINE = "line"
    TITLE = "title"
    SUBTITLE = "subtitle"
    FOOTER = "footer"
    PARAGRAPH = "paragraph"
    ORDERED_LIST = "ordered-list"
    UNORDERED_LIST = "unordered-list"
    LIST_ITEM = "list-item"
    LINK = "link"
    CAPTION = "caption"
    IMAGE = "image"
    BLOCK_QUOTE = "block-quote"
    BLOCK_CODE = "block-code"
    UNKNOWN = "unknown"
    SENTENCE = "sentence"
    TOKEN = "token"  # noqa: S105
    SPAN = "span"
    DIV = "div"
    PRE = "pre"
    STRONG = "strong"
    EMPHASIZED = "emphasized"
    UNDERLINED = "underlined"
    TELETYPE = "teletype"
    ARTICLE = "article"
    MAIN = "main"
    CHAPTER = "chapter"
    TEXT = "text"

    @staticmethod
    def from_html_tag(tagname: Optional[str]) -> Optional["DocTag"]:  # noqa: C901
        if tagname is None:
            return None

        name = tagname.lower().strip()

        if name == "p":
            return DocTag.PARAGRAPH
        elif name == "h1":
            return DocTag.H1
        elif name == "h2":
            return DocTag.H2
        elif name == "h3":
            return DocTag.H3
        elif name == "h4":
            return DocTag.H4
        elif name == "h5":
            return DocTag.H5
        elif name == "ul":
            return DocTag.UNORDERED_LIST
        elif name == "ol":
            return DocTag.ORDERED_LIST
        elif name == "li":
            return DocTag.LIST_ITEM
        elif name == "a":
            return DocTag.LINK
        elif name == "div":
            return DocTag.DIV
        elif name == "img":
            return DocTag.IMAGE
        elif name == "span":
            return DocTag.SPAN
        elif name == "pre":
            return DocTag.PRE
        elif name == "code":
            return DocTag.BLOCK_CODE
        elif name == "blockquote":
            return DocTag.BLOCK_QUOTE
        elif name == "strong":
            return DocTag.STRONG
        elif name == "b":
            return DocTag.STRONG
        elif name == "emph":
            return DocTag.EMPHASIZED
        elif name == "i":
            return DocTag.EMPHASIZED
        elif name == "u":
            return DocTag.UNDERLINED
        elif name == "tt":
            return DocTag.TELETYPE
        elif name == "article":
            return DocTag.ARTICLE
        elif name == "header":
            return DocTag.HEADER
        elif name == "footer":
            return DocTag.FOOTER
        elif name == "main":
            return DocTag.MAIN

        return None


class TokenTag(str, Enum):
    """A set of `name` constants for Tags with a `kind` of `TagKind.token`; appropriate for parsing-level ideas."""

    TEXT_WITH_WHITESPACE = "text-with-whitespace"
    TEXT = "text"
    WHITESPACE = "whitespace"
    HEAD = "head"
    LEFT_EDGE = "left-edge"
    RIGHT_EDGE = "right-edge"
    ENTITY_TYPE = "entity-type"
    ENTITY_IOB = "entity-iob"
    LEMMA = "lemma"
    NORMALIZED = "normalized"
    SHAPE = "shape"
    PREFIX = "prefix"
    SUFFIX = "suffix"
    IS_ALPHA = "is-alpha"
    IS_ASCII = "is-ascii"
    IS_DIGIT = "is-digit"
    IS_TITLE = "is-title"
    IS_PUNCT = "is-punct"
    IS_LEFT_PUNCT = "is-left-punct"
    IS_RIGHT_PUNCT = "is-right-punct"
    IS_SPACE = "is-space"
    IS_BRACKET = "is-bracket"
    IS_QUOTE = "is-quote"
    IS_CURRENCY = "is-currency"
    LIKE_URL = "like-url"
    LIKE_NUM = "like-num"
    LIKE_EMAIL = "like-email"
    IS_OUT_OF_VOCABULARY = "is-out-of-vocabulary"
    IS_STOPWORD = "is-stopword"
    LANGUAGE = "language"


class TagValueKey(str, Enum):
    """A set of key constants for the `value` object within a tag.."""

    # Catch-all for confidence, score, ranking
    SCORE = "score"

    # Catch-all for values of different types such as integers, floats, booleans, and strings
    VALUE = "value"

    # An array of floats or integers
    VECTOR_VALUE = "vector-value"

    # A float or integer
    NUMBER_VALUE = "number-value"

    # A bool
    BOOL_VALUE = "bool-value"

    # A string
    STRING_VALUE = "string-value"

    # Whether some annotation is direct ("Susan said 'Hi'")
    DIRECT = "direct"

    # Start time of a region of a document, in some other medium (seconds)
    START_TIME_S = "start-time-s"

    # End time of a region of a document, in some other medium (seconds)
    END_TIME_S = "end-time-s"

    # The normalized name of an entity
    ENTITY_NAME = "entity_name"

    # Timestamp. Can be used to provide a time-based sort-ordering for tags.
    TIMESTAMP_VALUE = "timestamp-value"


class GenerationTag(str, Enum):
    """A set of `name` constants for Tags with a `kind` of `TagKind.generation`."""

    # A generated summary of some region of a document
    SUMMARY = "summary"

    # A generated headline for some region of a document
    HEADLINE = "headline"

    # A generated "micro summary" of some region of a document
    GIST = "gist"

    # A generated completion using some region of the document as input
    PROMPT_COMPLETION = "prompt-completion"


class ProvenanceTag(str, Enum):
    """A set of `name` constants for Tags with a `kind` of `TagKind.provenance`."""

    # The speaker of a section of a document
    SPEAKER = "speaker"

    # The URL from which some section of a document was sourced
    URL = "url"

    # The File from which some section of a document was sourced
    FILE = "file"
