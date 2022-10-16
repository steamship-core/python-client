from importlib.metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

from .base import Configuration, MimeTypes, SteamshipError
from .data import (
    Block,
    DocTag,
    EmbeddingIndex,
    EmotionTag,
    File,
    Package,
    PackageInstance,
    PackageVersion,
    PluginInstance,
    PluginVersion,
    SentimentTag,
    Space,
    Tag,
    TagKind,
    TagValue,
    TokenTag,
)

from .client import Steamship  # isort:skip

__all__ = [
    "Steamship",
    "Configuration",
    "SteamshipError",
    "MimeTypes",
    "Package",
    "PackageInstance",
    "PackageVersion",
    "File",
    "Block",
    "Tag",
    "Space",
    "PluginInstance",
    "PluginVersion",
    "TagKind",
    "TokenTag",
    "SentimentTag",
    "EmotionTag",
    "DocTag",
    "EmbeddingIndex",
    "TagValue",
]
