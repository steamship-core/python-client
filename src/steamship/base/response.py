import time

from steamship.base.error import SteamshipError
from steamship.base.tasks import *

T = TypeVar('T')  # Declare type variable


@dataclass
class Response(IResponse, Generic[T]):
    expect: Type[T] = None
    task: Task = None
    data: T = None
    error: SteamshipError = None
    client: Any = None

    def update(self, response: "Response[T]"):
        if self.task is not None and response.task is not None:
            self.task.update(response.task)
        if response.data is not None:
            self.data = response.data
        self.error = response.error

    def wait(self, max_timeout_s: float = 60, retry_delay_s: float = 1):
        """Polls and blocks until the task has succeeded or failed (or timeout reached)."""
        start = time.time()
        if self.task is None or self.task.state == TaskStatus.failed:
            return

        self.check()
        if self.task is not None:
            if self.task.state == TaskStatus.succeeded or self.task.state == TaskStatus.failed:
                return
        else:
            return
        time.sleep(retry_delay_s)

        while time.time() - start < max_timeout_s:
            time.sleep(retry_delay_s)
            self.check()
            if self.task is not None:
                if self.task.state == TaskStatus.succeeded or self.task.state == TaskStatus.failed:
                    return
            else:
                return

    def check(self):
        if self.task is None:
            return
        req = TaskStatusRequest(
            self.task.taskId
        )
        resp = self.client.post(
            'task/status',
            payload=req,
            expect=self.expect
        )
        self.update(resp)

    def add_comment(self, externalId: str = None, externalType: str = None, externalGroup: str = None,
                    metadata: any = None) -> "Response[TaskComment]":
        if self.task is not None:
            return self.task.add_comment(externalId=externalId, externalType=externalType, externalGroup=externalGroup,
                                         metadata=metadata)

    def list_comments(self) -> "Response[TaskCommentList]":
        if self.task is not None:
            return self.task.list_comments()

    def delete_comment(self, comment: "TaskComment" = None) -> "Response[TaskComment]":
        if self.task is not None:
            return self.task.delete_comment(comment=comment)
