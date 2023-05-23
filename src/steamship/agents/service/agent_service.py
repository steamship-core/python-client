from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Union

from steamship import Block, Task, TaskState
from steamship.agents.base import Action, FinishAction
from steamship.agents.context.context import AgentContext
from steamship.agents.planner.base import Planner
from steamship.invocable import PackageService, post


def _is_running(task: Task) -> bool:
    task.refresh()
    return task.state not in [TaskState.succeeded, TaskState.failed]


class AgentService(PackageService, ABC):
    agent_context_identifier = (
        "_steamship_agent_contexts"  # probably want to include instance_handle...
    )
    planner: Planner

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    ###############################################
    # Tool selection / execution magic
    ###############################################

    def _next_action(self, context: AgentContext) -> Action:
        return self.planner.plan(context)

    @post("take_action")
    def take_action(self, context: AgentContext) -> Union[Action, FinishAction]:
        action = self._next_action(context)
        if isinstance(action, FinishAction):
            return action

        block_or_task = action.tool.run(action.tool_input, action.context)
        if isinstance(block_or_task, Task):
            context.in_progress.append((action, block_or_task))
            # self.upsert_context(context)

            for func in context.emit_funcs:
                func([Block(text=f"Status: Running {action}")], context.metadata)
            self.invoke_later(
                method="_steamship/run",
                arguments={"context": context},
                wait_on_tasks=[block_or_task],
            )
        else:
            output_blocks = action.tool.run(action.tool_input, context)
            action.tool_output = output_blocks
            context.completed_steps.append(action)
            # self.upsert_context(context)
            return action

    @post("_steamship/run")
    def run_agent(self, context: AgentContext):
        # first thing we must do is determine if we are still waiting on any pending executions
        # if so, reschedule run_agent for later.
        last_known_pending_tasks = context.in_progress
        completed_bindings_and_tasks = [
            Tuple[tb, t] for tb, t in last_known_pending_tasks if not _is_running(t)
        ]
        for action, task in completed_bindings_and_tasks:
            task.refresh()
            action.tool_output = task.output.blocks
            context.completed_steps.append(action)
        # self.upsert_context(context)
        running_tasks = [t for _, t in last_known_pending_tasks if _is_running(t)]
        if len(running_tasks) > 0:
            # todo: do we need to do anything with this pending task?
            self.invoke_later(
                method="_steamship/run", arguments={"context": context}, wait_on_tasks=running_tasks
            )
            return

        # at this stage in run_agent, we have no more running tasks. we have 0 or more completed steps.
        # we must now select the next step
        action = self.take_action(context)
        while not isinstance(action, FinishAction):
            action = self.take_action(context)

        for func in context.emit_funcs:
            func(action.output, context.metadata)
        # self.unload_context(context_id=context.id)

    @abstractmethod
    def create_response(self, context: AgentContext) -> Optional[List[Block]]:
        raise NotImplementedError
