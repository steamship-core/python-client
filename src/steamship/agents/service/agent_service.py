import logging

from steamship import SteamshipError, Task
from steamship.agents.logging import AgentLogging
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
            outputs = ",".join([f"{b.as_llm_input()}" for b in blocks_or_task])
            logging.info(
                f"Tool {action.tool.name}: ({outputs})",
                extra={
                    AgentLogging.TOOL_NAME: action.tool.name,
                    AgentLogging.IS_MESSAGE: True,
                    AgentLogging.MESSAGE_TYPE: AgentLogging.OBSERVATION,
                    AgentLogging.MESSAGE_AUTHOR: AgentLogging.AGENT,
                },
            )
            action.output = blocks_or_task
            context.completed_steps.append(action)

    def run_agent(self, agent: Agent, context: AgentContext):
        action = agent.next_action(context=context)
        while not isinstance(action, FinishAction):
            # TODO: Arrive at a solid design for the details of this structured log object
            inputs = ",".join([f"{b.as_llm_input()}" for b in action.input])
            logging.info(
                f"Running Tool {action.tool.name} ({inputs})",
                extra={
                    AgentLogging.TOOL_NAME: action.tool.name,
                    AgentLogging.IS_MESSAGE: True,
                    AgentLogging.MESSAGE_TYPE: AgentLogging.ACTION,
                    AgentLogging.MESSAGE_AUTHOR: AgentLogging.AGENT,
                },
            )
            self.run_action(action=action, context=context)
            action = agent.next_action(context=context)
            # TODO: Arrive at a solid design for the details of this structured log object
            logging.info(
                f"Next Tool: {action.tool.name}",
                extra={
                    AgentLogging.TOOL_NAME: action.tool.name,
                    AgentLogging.IS_MESSAGE: False,
                    AgentLogging.MESSAGE_TYPE: AgentLogging.ACTION,
                    AgentLogging.MESSAGE_AUTHOR: AgentLogging.AGENT,
                },
            )

        context.completed_steps.append(action)
        for func in context.emit_funcs:
            func(action.output, context.metadata)
