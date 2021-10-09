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

    bio.convert().wait()

    res = bio.query().data
    assert(res == 0)
    
    

    bio.delete()
    # for file in files:
    #   file.delete()

    # contract.insert(file)
    # index = contract.parse().embed()

    # index.query("Who focuses on enterprise investments?")

    

