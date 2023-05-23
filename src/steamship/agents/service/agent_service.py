import logging

from steamship import SteamshipError, Task
from steamship.agents.schema import Action, Agent, FinishAction
from steamship.agents.schema.context import AgentContext
from steamship.invocable import PackageService


class AgentService(PackageService):
    """AgentService is a Steamship Package that can use an Agent, Tools, and a provided AgentContext to
    respond to user input."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    ###############################################
    # Tool selection / execution
    ###############################################

    def run_action(self, action: Action, context: AgentContext):
        if isinstance(action, FinishAction):
            return

        blocks_or_task = action.tool.run(tool_input=action.input, context=context)
        if isinstance(blocks_or_task, Task):
            raise SteamshipError(
                "Tools return Tasks are not yet supported (but will be soon). "
                "Please use synchronous Tasks (Tools that return List[Block] for now."
            )
        else:
            action.output = blocks_or_task
            context.completed_steps.append(action)

    def run_agent(self, agent: Agent, context: AgentContext):
        action = agent.next_action(context=context)
        while not isinstance(action, FinishAction):
            # TODO: logging?
            logging.info(f"running action: {action}")
            self.run_action(action=action, context=context)
            action = agent.next_action(context=context)
            # TODO: logging?
            logging.info(f"next action: {action}")

        context.completed_steps.append(action)
        for func in context.emit_funcs:
            func(action.output, context.metadata)
