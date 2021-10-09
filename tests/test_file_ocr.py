from nludb.types.async_task import NludbTaskStatus
import pytest
from os import path
from .helpers import _random_name, _nludb
from nludb import NLUDB, BlockTypes, FileFormats, OcrModels

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"


def test_image_upload():
    nludb = _nludb()
    test_filename = path.join(
      path.dirname(path.realpath(__file__)),
      'test_img.png'
    )
    with open(test_filename, "rb") as f:
      name_c = "{}.png".format(_random_name())
      c = nludb.upload(
          name=name_c,
          content=f
      )
      assert(c.id is not None)
      assert(c.name == name_c)
      assert(c.format == FileFormats.PNG)

      c.convert(ocrModel = OcrModels.MS_VISION_DEFAULT)
      c.delete()
