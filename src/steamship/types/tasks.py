import logging

from steamship import __version__
from steamship.types.base import Response, ListTaskCommentRequest, ListTaskCommentResponse
from steamship.client.base import ApiBase
from steamship.types.model import *

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

class Tasks:
  """Asynchronous background task (and task feedback) management.
  """

  def __init__(self, client: ApiBase):
    self.client = client

  def list_comments(
    self,
    taskId: str = None,
    externalId: str = None,
    externalType: str = None,
    externalGroup: str = None
  ) -> Response[ListTaskCommentResponse]:
    return self.client.post(
      'task/comment/list',
      ListTaskCommentRequest(
        taskId=taskId,
        externalId=externalId,
        externalType=externalType,
        externalGroup=externalGroup
      ),
      expect=ListTaskCommentResponse
    )
