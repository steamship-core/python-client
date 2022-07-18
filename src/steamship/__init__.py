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
    App,
    AppInstance,
    AppVersion,
    Block,
    DocTag,
    EmbeddingIndex,
    File,
    PluginInstance,
    PluginVersion,
    Space,
    Tag,
    TagKind,
    TextTag,
)

from .client import Steamship  # isort:skip

__all__ = [
    "Steamship",
    "Configuration",
    "SteamshipError",
    "MimeTypes",
    "App",
    "AppInstance",
    "AppVersion",
    "File",
    "Block",
    "Tag",
    "Space",
    "PluginInstance",
    "PluginVersion",
    "TagKind",
    "TextTag",
    "DocTag",
    "EmbeddingIndex",
]
