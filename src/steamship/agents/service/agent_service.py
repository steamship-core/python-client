from typing import List, Optional, Tuple, Union

from steamship import Block, Task, TaskState
from steamship.agents.base import Action, AgentContext, FinishAction, Metadata
from steamship.agents.planner.base import Planner
from steamship.agents.tool import Tool
from steamship.invocable import PackageService, post
from steamship.utils.kv_store import KeyValueStore


def _is_running(task: Task) -> bool:
    task.refresh()
    return task.state not in [TaskState.succeeded, TaskState.failed]


class AgentService(PackageService):
    agent_context_identifier = (
        "_steamship_agent_contexts"  # probably want to include instance_handle...
    )
    context_cache: KeyValueStore
    planner: Planner

    tools: List[Tool] = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context_cache = KeyValueStore(
            client=self.client, store_identifier=self.agent_context_identifier
        )

    ##################################################
    # Context-related actions for load/persist/delete
    ##################################################

    def upsert_context(self, context: AgentContext):
        # self.context_cache.set(context.id, "foo")
        pass

    def new_context_with_metadata(self, md: Metadata) -> AgentContext:
        ctx = AgentContext()
        ctx.metadata = md
        self.upsert_context(ctx)
        return ctx

    def load_context(self, context_id: str) -> Optional[AgentContext]:
        maybe_context = self.context_cache.get(context_id)
        if not maybe_context:
            return None
        return AgentContext.parse_obj(maybe_context)

    def unload_context(self, context_id: str):
        self.context_cache.delete(context_id)

    ###############################################
    # Tool selection / execution magic
    ###############################################

    def _next_action(self, context: AgentContext) -> Action:
        return self.planner.plan(self.tools, context)

    @post("take_action")
    def take_action(self, context: AgentContext) -> Union[Action, FinishAction]:
        action = self._next_action(context)
        if isinstance(action, FinishAction):
            return action

        block_or_task = action.tool.run(action.tool_input, action.context)
        if isinstance(block_or_task, Task):
            context.in_progress.append((action, block_or_task))
            self.upsert_context(context)

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
            self.upsert_context(context)
            return action

    @post("_steamship/run")
    def run_agent(self, context: AgentContext):

        # first thing we must do is determine if we are still waiting on any pending executions
        # if so, reschedule run_agent for later.
        last_known_pending_tasks = context.in_progress
        completed_bindings_and_tasks = [
            Tuple[tb, t] for tb, t in last_known_pending_tasks if not _is_running(t)
        ]
        for (action, task) in completed_bindings_and_tasks:
            task.refresh()
            action.tool_output = task.output.blocks
            context.completed_steps.append(action)
        self.upsert_context(context)
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
        self.unload_context(context_id=context.id)
