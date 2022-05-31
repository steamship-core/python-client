import logging
from typing import List

from pydantic import BaseModel, Field

from steamship.base import Client, Response, TaskComment

_logger = logging.getLogger(__name__)


class Tasks(BaseModel):
    """Asynchronous background task (and task feedback) management."""

    client: Client = Field(None, repr=False)

    def __init__(self, client: Client):
        super().__init__()
        self.client = client

    def list_comments(
        self,
        task_id: str = None,
        external_id: str = None,
        external_type: str = None,
        external_group: str = None,
    ) -> Response[List[TaskComment]]:
        return TaskComment.list(
            client=self.client,
            task_id=task_id,
            external_id=external_id,
            external_type=external_type,
            external_group=external_group,
        )
