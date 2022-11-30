from enum import Enum


class Skill(str, Enum):
    ENTITIES = "entities"
    SUMMARY = "summary"
    SENTIMENTS = "sentiments"
    EMOTIONS = "emotions"
    TOPICS = "topics"
    HIGHLIGHTS = "highlights"
    KEYWORDS = "keywords"
