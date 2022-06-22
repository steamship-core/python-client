from __future__ import annotations

import time
from typing import Any, Generic, Type, TypeVar

from pydantic.generics import GenericModel

from steamship.base.error import SteamshipError
from steamship.base.tasks import Task, TaskState, TaskStatusRequest
from steamship.base.utils import to_camel

T = TypeVar("T")  # Declare type variable


class Response(GenericModel, Generic[T]):
    expect: Type[T] = None
    task: Task = None
    data_: T = None
    error: SteamshipError = None
    client: Any = None

    class Config:
        arbitrary_types_allowed = True  # This is required to support SteamshipError
        alias_generator = to_camel
        allow_population_by_field_name = True

    @property
    def data(self):
        if self.error:
            raise self.error
        if self.task is not None:
            if self.task.state == TaskState.failed:
                raise SteamshipError(
                    "Asynchronous call failed. No error available. Please contact support."
                )
            if self.task.state != TaskState.succeeded and self.data_ is None:
                raise SteamshipError(
                    "Data not available yet for asynchronous call. Please call .wait() before accessing .data"
                )
        return self.data_

    def update(self, response: Response[T]):
        if self.task is not None and response.task is not None:
            self.task.update(response.task)
        if response.data_ is not None:
            self.data_ = response.data_
        self.error = response.error

    def wait(self, max_timeout_s: float = 60, retry_delay_s: float = 1):
        """Polls and blocks until the task has succeeded or failed (or timeout reached)."""
        if self.task is None:
            return
        t0 = time.perf_counter()
        while time.perf_counter() - t0 < max_timeout_s and self.task.state not in (
            TaskState.succeeded,
            TaskState.failed,
        ):
            self.refresh()
            time.sleep(retry_delay_s)

    def refresh(self):
        if self.task is not None:
            req = TaskStatusRequest(taskId=self.task.task_id)
            resp = self.client.post("task/status", payload=req, expect=self.expect)
            self.update(resp)
