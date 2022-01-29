import sys

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # type: ignore # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

from .client.client import Steamship
from .types.embedding_index import EmbeddingIndex
from .types.classifier import Classifier
from .types.corpus import Corpus
from .types.space import Space
from .types.file import File
from .types.block import BlockTypes, Block
from .types.app import App
from .types.app_instance import AppInstance
from .types.app_version import AppVersion
