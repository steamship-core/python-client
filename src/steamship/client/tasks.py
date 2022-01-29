import logging

from steamship.base.response import TaskCommentList, TaskComment
from steamship.plugin.plugin import *

__copyright__ = "Steamship"
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
    ) -> Response[TaskCommentList]:
        return TaskComment.list(
            client=self.client,
            taskId=taskId,
            externalId=externalId,
            externalType=externalType,
            externalGroup=externalGroup
        )
