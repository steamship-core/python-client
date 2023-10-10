from importlib.metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

from .base import (
    Configuration,
    MimeTypes,
    RuntimeEnvironments,
    SteamshipError,
    Task,
    TaskState,
    check_environment,
)
from .data import (
    Block,
    DocTag,
    EmbeddingIndex,
    File,
    Package,
    PackageInstance,
    PackageVersion,
    PluginInstance,
    PluginVersion,
    Tag,
    Workspace,
)

from .client import Steamship  # isort:skip

SUPPORTED_PYTHON_VERSIONS = [(3, 10)]
SUPPORTED_PYTHON_VERSION_NAMES = [f"{major}.{minor}" for major, minor in SUPPORTED_PYTHON_VERSIONS]


def is_supported_python_version() -> bool:
    import sys

    major, minor, _, _, _ = sys.version_info
    for supported_version in SUPPORTED_PYTHON_VERSIONS:
        s_major, s_minor = supported_version
        supported = (major == s_major) and (s_minor is None or s_minor == minor)
        if supported:
            break
    else:
        return False
    return True


__all__ = [
    "Steamship",
    "Configuration",
    "SteamshipError",
    "MimeTypes",
    "Package",
    "PackageInstance",
    "PackageVersion",
    "File",
    "Task",
    "TaskState",
    "Block",
    "Tag",
    "Workspace",
    "PluginInstance",
    "PluginVersion",
    "DocTag",
    "EmbeddingIndex",
    "check_environment",
    "RuntimeEnvironments",
]
