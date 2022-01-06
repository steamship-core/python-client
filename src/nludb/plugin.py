import logging
import json
import re
from typing import Union, List, Dict, Tuple

from nludb import __version__
from nludb.api.base import ApiBase
from nludb.types.base import Response
from nludb.types.file import *
from nludb.types.parsing_models import ParsingModels
from nludb.types.tag import *
from nludb.types.tag import TagObjectRequest

_logger = logging.getLogger(__name__)

class PluginVersion:
  pass

class Plugin:
  """A service.
  """
