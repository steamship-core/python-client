from nludb.types.async_task import NludbTaskStatus
import pytest
from os import path
from .helpers import _random_name, _nludb
from nludb import NLUDB, BlockTypes, FileFormats

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"


def test_file_scrape():
    nludb = _nludb()

    VC_BIOS = [
      "https://www.indexventures.com/team/nina-achadjian/",
      "https://www.indexventures.com/team/chris-ahn/"
    ]

    bio = nludb.scrape(VC_BIOS[0])


    for file in files:
      file.delete()

