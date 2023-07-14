import logging
import uuid
from typing import List, Optional

from steamship import Block, SteamshipError, Task
from steamship.agents.llms import OpenAI
from steamship.agents.logging import AgentLogging
from steamship.agents.schema import Action, Agent, FinishAction
from steamship.agents.schema.context import AgentContext, Metadata
from steamship.agents.utils import with_llm
from steamship.invocable import PackageService, post


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
        # first, clear any prior agent steps from set of completed steps
        # this will allow the agent to select tools/dispatch actions based on a new context
        context.completed_steps = []
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
        output_text_length = 0
        if action.output is not None:
            output_text_length = sum([len(block.text or "") for block in action.output])
        logging.info(
            f"Completed agent run. Result: {len(action.output or [])} blocks. {output_text_length} total text length. Emitting on {len(context.emit_funcs)} functions."
        )
        for func in context.emit_funcs:
            logging.info(f"Emitting via function: {func.__name__}")
            func(action.output, context.metadata)

    @post("prompt")
    def prompt(self, prompt: Optional[str] = None, **kwargs) -> List[Block]:
        """Run an agent with the provided text as the input."""
        prompt = prompt or kwargs.get("question")

        # AgentContexts serve to allow the AgentService to run agents
        # with appropriate information about the desired tasking.
        # Here, we create a new context on each prompt, and append the
        # prompt to the message history stored in the context.
        context_id = uuid.uuid4()
        context = AgentContext.get_or_create(self.client, {"id": f"{context_id}"})
        context.chat_history.append_user_message(prompt)

        # Add a default LLM
        context = with_llm(context=context, llm=OpenAI(client=self.client, model_name="gpt-4-0613"))

        # AgentServices provide an emit function hook to access the output of running
        # agents and tools. The emit functions fire at after the supplied agent emits
        # a "FinishAction".
        #
        # Here, we show one way of accessing the output in a synchronous fashion. An
        # alternative way would be to access the final Action in the `context.completed_steps`
        # after the call to `run_agent()`.
        output_blocks = []

        def sync_emit(blocks: List[Block], meta: Metadata):
            nonlocal output_blocks
            output_blocks.extend(blocks)

        context.emit_funcs.append(sync_emit)

        # Get the agent
        agent: Optional[Agent] = None
        if hasattr(self, "agent"):
            agent = self.agent
        elif hasattr(self, "_agent"):
            agent = self._agent

        if not agent:
            raise SteamshipError(
                message="No Agent object found in the Agent Service. "
                "Please name it either self.agent or self._agent."
            )

        self.run_agent(agent, context)

        # Now append the output blocks to the chat history
        # TODO: It seems like we've been going from block -> not block -> block here. Opportunity to optimize.
        for output_block in output_blocks:
            # Need to make the output blocks public here so that they can be copied to the chat history.
            # They generally need to be public anyway for the REPL to be able to show a clickable link.
            output_block.set_public_data(True)
            context.chat_history.append_assistant_message(
                text=output_block.text,
                tags=output_block.tags,
                url=output_block.raw_data_url or output_block.url or output_block.content_url,
                mime_type=output_block.mime_type,
            )

        # Return the response as a set of multi-modal blocks.
        return output_blocks
