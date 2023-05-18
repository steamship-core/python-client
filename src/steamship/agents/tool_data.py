import json
from abc import ABC
from typing import Any, List, Optional

from pydantic import BaseModel

from steamship import Block, File, Steamship, SteamshipError, Task, TaskState

Tool_ = Any


class ToolData(BaseModel, ABC):
    """Represents a list of blocks, which may not yet exist."""

    # The list of blocks, inline.
    inline_value: Optional[List[Block]] = None

    # The list of blocks, as the contents of a file.
    file_id: Optional[str] = None

    # The list of blocks, as the output of a task.
    task_id: Optional[str] = None

    def state(self, client: Steamship) -> TaskState:
        """Return the state of this BlockList.

        This overloading of TaskState is slightly awkward, but more accurate than an is_ready bool.
        """
        if self.inline_value:
            return TaskState.succeeded
        elif self.file_id:
            return TaskState.succeeded
        elif self.task_id:
            task = Task.get(client, _id=self.task_id)
            return task.state

    def value(self, client: Steamship, post_processor_tool: Tool_ = None) -> List[Block]:
        """Synchronously return the set of blocks underlying this BlockList.

        If that set of blocks is unavailable, an Exception will be thrown. First check `state() == succeeded` to verify
        the list is ready.
        """
        if self.inline_value is not None:
            # Allows the empty-list intentionally.
            return self.inline_value
        elif self.file_id:
            file = File.get(client, _id=self.file_id)
            return file.blocks
        elif self.task_id:
            task = Task.get(client, _id=self.task_id)
            if task.state != TaskState.succeeded:
                raise SteamshipError(
                    message=f"Attempted to load BlockList from non-succeeded Task {self.task_id}. Task had state {task.state}"
                )

            if post_processor_tool:
                return post_processor_tool(task)
            else:
                try:
                    return json.loads(task.output)
                except BaseException as e:
                    raise SteamshipError(
                        message=f"Error deserializing BlockList from Task.output {self.task_id}",
                        error=e,
                    )
        else:
            raise SteamshipError(message="Unable to fetch value from BlockList")

    def outstanding_task_dependencies(self, client: Steamship) -> Optional[List[Task]]:
        """Return any tasks that this ToolData depends upon to be considered ready for access."""
        if not self.task_id:
            return None

        task = Task.get(client, _id=self.task_id)
        if task.state in [TaskState.succeeded, TaskState.failed]:
            return None

        return [task]
