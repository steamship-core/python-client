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
      ).data
      assert(c.id is not None)
      assert(c.name == name_c)
      assert(c.mimeType == FileFormats.PNG)

      convertResp = c.convert(model = OcrModels.MS_VISION_DEFAULT)
      assert(convertResp.error is None)
      convertResp.wait()
      assert(convertResp.data is not None)

      q1 = c.query().data
      assert(len(q1.blocks) == 3)


      c.delete()
