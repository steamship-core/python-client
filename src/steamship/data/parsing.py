from dataclasses import dataclass
from typing import List, Dict

from steamship.base.client import Client

MatcherClause = Dict[str, any]
Matcher = List[MatcherClause]


@dataclass
class TokenMatcher():
    label: str = None
    patterns: List[Matcher] = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "TokenMatcher":
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
    def from_dict(d: any, client: Client = None) -> "PhraseMatcher":
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
    def from_dict(d: any, client: Client = None) -> "DependencyMatcher":
        return DependencyMatcher(
            label=d.get("label", None),
            patterns=(d.get("patterns", []) or [])
        )
