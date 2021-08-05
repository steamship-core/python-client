import sys

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

from .nludb import NLUDB
from .embedding_index import EmbeddingIndex
from .classifier import Classifier
from .types.embedding_models import EmbeddingModels
from .types.classifier_models import ClassifierModels
from .types.parsing_models import ParsingModels
from .file import File
from .types.model import ModelType, ModelAdapterType, LimitUnit, Model
from .types.block_types import BlockTypes
from .types.file_formats import FileFormats