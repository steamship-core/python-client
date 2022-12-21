from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import Field

from steamship import SteamshipError
from steamship.base.client import Client
from steamship.base.model import CamelModel
from steamship.base.request import Request
from steamship.base.response import Response
from steamship.data.tags.tag_constants import TagKind, TagValueKey


class TagQueryRequest(Request):
    tag_filter_query: str


class Tag(CamelModel):
    # Steamship client.
    client: Client = Field(None, exclude=True)

    # ID of the tag in the database.
    id: str = None

    # ID of the file associated with the tag.
    file_id: str = None

    # ID of the block associated with the tag. If not None, `start_idx` and `end_idx` should be set.
    block_id: Optional[str] = None

    # The kind of tag. See the ``TagKind`` enum class for suggestions.
    kind: Union[TagKind, str] = None  # E.g. ner

    # The name of tag. See the ``DocTag``, ``TokenTag``, etc enum classes for suggestions.
    name: Optional[str] = None  # E.g. person

    # The value payload of the tag. Always a JSON-style object.
    value: Optional[Dict[Union[TagValueKey, str], Any]] = None

    # Character index in associated block of the start of the span of text this tag comments upon. Start-inclusive.
    start_idx: Optional[int] = None

    # Character index in associated block of the end of the span of text this tag comments upon. End-exclusive.
    end_idx: Optional[int] = None

    # The text covered by the tag.
    # Note:
    #   The text will not always be materialized into the tag object
    #   itself; you may have to fetch it with file.text[tag.start_idx:tag.end_idx]
    # Note:
    #   Changing this field will not result in changes to Steamship's database.
    #   TODO(ted): Consider refactoring as a read-only property.
    #
    text: Optional[str] = None

    class DeleteRequest(Request):
        id: str = None
        file_id: str = None
        block_id: str = None

    class ListRequest(Request):
        file_id: str = None
        block_id: str = None

    class ListResponse(Response):
        tags: List[Tag] = None

    @staticmethod
    def create(
        client: Client,
        file_id: str = None,
        block_id: str = None,
        kind: str = None,
        name: str = None,
        start_idx: int = None,
        end_idx: int = None,
        value: Dict[str, Any] = None,
    ) -> Tag:
        req = Tag(
            file_id=file_id,
            block_id=block_id,
            kind=kind,
            name=name,
            start_idx=start_idx,
            end_idx=end_idx,
            value=value,
        )
        return client.post("tag/create", req, expect=Tag)

    def delete(self) -> Tag:
        return self.client.post(
            "tag/delete",
            Tag.DeleteRequest(id=self.id, file_id=self.file_id, block_id=self.block_id),
            expect=Tag,
        )

    def index(self, plugin_instance: Any = None):
        """Index this tag."""
        return plugin_instance.insert(self)

    @staticmethod
    def query(
        client: Client,
        tag_filter_query: str,
    ) -> TagQueryResponse:
        req = TagQueryRequest(tag_filter_query=tag_filter_query)
        res = client.post(
            "tag/query",
            payload=req,
            expect=TagQueryResponse,
        )
        return res


class TimestampTag(Tag):
    def __init__(
        self,
        start_time_s: float,
        end_time_s: float,
        start_idx: Optional[int] = None,
        end_idx: Optional[int] = None,
        value: Optional[Dict[str, Any]] = None,
    ):
        value = value or {}
        super().__init__(
            kind=TagKind.TIMESTAMP,
            start_idx=start_idx,
            end_idx=end_idx,
            value={
                **value,
                TagValueKey.START_TIME_S: start_time_s,
                TagValueKey.END_TIME_S: end_time_s,
            },
        )


class TokenizationTag(Tag):
    class Type(str, Enum):
        PARAGRAPH = "paragraph"
        SENTENCE = "sentence"
        WORD = "word"
        CHARACTER = "character"

    def __init__(
        self,
        type=Type,
        start_idx: Optional[int] = None,
        end_idx: Optional[int] = None,
        value: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            kind=TagKind.TOKENIZATION, name=type, start_idx=start_idx, end_idx=end_idx, value=value
        )


class SummaryTag(Tag):
    def __init__(
        self,
        summary: str,
        start_idx: Optional[int] = None,
        end_idx: Optional[int] = None,
        value: Optional[Dict[str, Any]] = None,
    ):
        value = value or {}
        super().__init__(
            kind=TagKind.SUMMARY,
            start_idx=start_idx,
            end_idx=end_idx,
            value={**value, TagValueKey.VALUE: summary},
        )


class TopicTag(Tag):
    def __init__(
        self,
        topic: str,
        start_idx: Optional[int] = None,
        end_idx: Optional[int] = None,
        value: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            kind=TagKind.TOPIC, name=topic, start_idx=start_idx, end_idx=end_idx, value=value
        )


class EmotionTag(Tag):
    class Emotion(str, Enum):
        POSITIVE = "positive"
        NEUTRAL = "neutral"
        NEGATIVE = "negative"
        HAPPINESS = "happiness"
        SADNESS = "sadness"
        JOY = "joy"
        LOVE = "love"
        ANGER = "anger"
        FEAR = "fear"
        SURPRISE = "surprise"
        HUMOR = "humor"
        CONCERN = "concern"
        SERIOUSNESS = "seriousness"
        SCORE = "score"

    def __init__(
        self,
        emotion: Emotion,
        start_idx: Optional[int] = None,
        end_idx: Optional[int] = None,
        value: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            kind=TagKind.EMOTION, name=emotion, start_idx=start_idx, end_idx=end_idx, value=value
        )


class IntentTag(Tag):
    class Intent(str, Enum):
        SALUTATION = "salutation"
        PRAISE = "praise"
        COMPLAINT = "complaint"
        QUESTION = "question"
        REQUEST = "request"
        EXPLANATION = "explanation"
        SCHEDULING_REQUEST = "scheduling-request"
        ARE_YOU_THERE = "are-you-there"
        REVISITING_TOPIC = "revisiting-topic"

    def __init__(
        self,
        intent: Intent,
        start_idx: Optional[int] = None,
        end_idx: Optional[int] = None,
        value: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            kind=TagKind.INTENT, name=intent, start_idx=start_idx, end_idx=end_idx, value=value
        )


class EntityTag(Tag):
    class EntityType(str, Enum):
        PERSON = "person"
        ORGANIZATION = "organization"
        PRODUCT = "product"
        LOCATION = "location"
        DATE = "date"
        TIME = "time"
        MONEY = "money"
        PERCENT = "percent"
        FACILITY = "facility"
        GEO_POLITICAL_ENTITY = "geo-political-entity"

    def __init__(
        self,
        entity_name: str,
        entity_type: EntityType,
        start_idx: Optional[int] = None,
        end_idx: Optional[int] = None,
        value: Optional[Dict[str, Any]] = None,
    ):
        if TagValueKey.ENTITY_NAME in value:
            raise SteamshipError(
                f"The value of your EntityTag cannot contain the key {TagValueKey.ENTITY_NAME}."
            )
        super().__init__(
            kind=TagKind.ENTITY,
            name=entity_type,
            start_idx=start_idx,
            end_idx=end_idx,
            value={**value, TagValueKey.ENTITY_NAME: entity_name},
        )


class SentimentTag(Tag):
    class Sentiment(str, Enum):
        POSITIVE = "positive"
        NEUTRAL = "neutral"
        NEGATIVE = "negative"
        SCORE = "score"

    def __init__(
        self,
        sentiment: Sentiment,
        start_idx: Optional[int] = None,
        end_idx: Optional[int] = None,
        value: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            kind=TagKind.ENTITY, name=sentiment, start_idx=start_idx, end_idx=end_idx, value=value
        )


class TagQueryResponse(Response):
    tags: List[Tag]


Tag.ListResponse.update_forward_refs()
TimestampTag.update_forward_refs()
TopicTag.update_forward_refs()
SummaryTag.update_forward_refs()
TokenizationTag.update_forward_refs()
SentimentTag.update_forward_refs()
EntityTag.update_forward_refs()
IntentTag.update_forward_refs()
EmotionTag.update_forward_refs()
