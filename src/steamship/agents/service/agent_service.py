import logging
import uuid
from typing import List, Optional

from steamship import Block, SteamshipError, Task
from steamship.agents.llms.openai import ChatOpenAI, OpenAI
from steamship.agents.logging import AgentLogging
from steamship.agents.schema import Action, Agent, FinishAction
from steamship.agents.schema.context import AgentContext, Metadata
from steamship.agents.utils import with_llm
from steamship.invocable import PackageService, post


class AgentService(PackageService):
    """AgentService is a Steamship Package that can use an Agent, Tools, and a provided AgentContext to
    respond to user input."""

    agent: Optional[Agent]
    """The default agent for this agent service."""

    use_llm_cache: bool
    """Whether or not to cache LLM calls (for tool selection/direct responses) by default."""

    use_action_cache: bool
    """Whether or not to cache agent Actions (for tool runs) by default."""

    max_actions_per_run: int
    """The maximum number of actions to permit while the agent is reasoning.

    This is intended primarily to act as a backstop to prevent a condition in which the Agent decides to loop endlessly
    on tool runs that consume resources with a cost-basis (e.g. prompt completions, embedding operations, vector lookups)
    """

    def __init__(
        self,
        use_llm_cache: Optional[bool] = False,
        use_action_cache: Optional[bool] = False,
        max_actions_per_run: Optional[int] = 5,
        agent: Optional[Agent] = None,
        **kwargs,
    ):
        self.use_llm_cache = use_llm_cache
        self.use_action_cache = use_action_cache
        self.max_actions_per_run = max_actions_per_run
        self.agent = agent
        super().__init__(**kwargs)

    ###############################################
    # Tool selection / execution
    ###############################################

    def next_action(self, agent: Agent, input_blocks: List[Block], context: AgentContext) -> Action:
        action: Action = None
        if context.llm_cache:
            action = context.llm_cache.lookup(key=input_blocks)
        if action:
            logging.info(
                f"Using cached response: calling {action.tool}.",
                extra={
                    AgentLogging.TOOL_NAME: "LLM",
                    AgentLogging.IS_MESSAGE: True,
                    AgentLogging.MESSAGE_TYPE: AgentLogging.OBSERVATION,
                    AgentLogging.MESSAGE_AUTHOR: AgentLogging.AGENT,
                },
            )
        else:
            inputs = ",".join([f"{b.as_llm_input()}" for b in input_blocks])
            logging.info(
                f"Prompting LLM with: ({inputs})",
                extra={
                    AgentLogging.TOOL_NAME: "LLM",
                    AgentLogging.IS_MESSAGE: True,
                    AgentLogging.MESSAGE_TYPE: AgentLogging.PROMPT,
                    AgentLogging.MESSAGE_AUTHOR: AgentLogging.AGENT,
                },
            )
            action = agent.next_action(context=context)
            if context.llm_cache:
                context.llm_cache.update(key=input_blocks, value=action)
        return action

    def run_action(self, agent: Agent, action: Action, context: AgentContext):
        if isinstance(action, FinishAction):
            return

        if not agent:
            raise SteamshipError(
                "Missing agent. Not able to run action on behalf of missing agent."
            )

        if context.action_cache:
            # if cache and action is cached, use it. otherwise proceed normally.
            if output_blocks := context.action_cache.lookup(key=action):
                outputs = ",".join([f"{b.as_llm_input()}" for b in output_blocks])
                logging.info(
                    f"Tool {action.tool}: ({outputs}) [cached]",
                    extra={
                        AgentLogging.TOOL_NAME: action.tool,
                        AgentLogging.IS_MESSAGE: True,
                        AgentLogging.MESSAGE_TYPE: AgentLogging.OBSERVATION,
                        AgentLogging.MESSAGE_AUTHOR: AgentLogging.AGENT,
                    },
                )
                action.output = output_blocks
                context.completed_steps.append(action)
                return

        tool = next((tool for tool in agent.tools if tool.name == action.tool), None)
        if not tool:
            raise SteamshipError(
                f"Could not find tool '{action.tool}' for action. Not able to run."
            )

        # TODO: Arrive at a solid design for the details of this structured log object
        inputs = ",".join([f"{b.as_llm_input()}" for b in action.input])
        logging.info(
            f"Running Tool {action.tool} ({inputs})",
            extra={
                AgentLogging.TOOL_NAME: action.tool,
                AgentLogging.IS_MESSAGE: True,
                AgentLogging.MESSAGE_TYPE: AgentLogging.ACTION,
                AgentLogging.MESSAGE_AUTHOR: AgentLogging.AGENT,
            },
        )
        blocks_or_task = tool.run(tool_input=action.input, context=context)
        if isinstance(blocks_or_task, Task):
            raise SteamshipError(
                "Tools return Tasks are not yet supported (but will be soon). "
                "Please use synchronous Tasks (Tools that return List[Block] for now."
            )
        else:
            outputs = ",".join([f"{b.as_llm_input()}" for b in blocks_or_task])
            logging.info(
                f"Tool {action.tool}: ({outputs})",
                extra={
                    AgentLogging.TOOL_NAME: action.tool,
                    AgentLogging.IS_MESSAGE: True,
                    AgentLogging.MESSAGE_TYPE: AgentLogging.OBSERVATION,
                    AgentLogging.MESSAGE_AUTHOR: AgentLogging.AGENT,
                },
            )
            action.output = blocks_or_task
            context.completed_steps.append(action)
            if context.action_cache:
                context.action_cache.update(key=action, value=action.output)

    def run_agent(self, agent: Agent, context: AgentContext):
        # first, clear any prior agent steps from set of completed steps
        # this will allow the agent to select tools/dispatch actions based on a new context
        context.completed_steps = []

        action = self.next_action(
            agent=agent, input_blocks=[context.chat_history.last_user_message], context=context
        )

        number_of_actions_run = 0

        while not isinstance(action, FinishAction):
            # Throw an error if we've exceeded our action budget.
            if number_of_actions_run >= self.max_actions_per_run:
                raise SteamshipError(
                    message=(
                        f"Agent reached its Action budget of {self.max_actions_per_run} without arriving at a response. If you are the developer, checking the logs may reveal it was selecting unhelpful tools or receiving unhelpful responses from them."
                    )
                )

            # Run the next action
            self.run_action(agent=agent, action=action, context=context)
            number_of_actions_run += 1

            # Select a new next_action and log it
            action = self.next_action(agent=agent, input_blocks=action.output, context=context)

            # TODO: Arrive at a solid design for the details of this structured log object
            logging.info(
                f"Next Tool: {action.tool}",
                extra={
                    AgentLogging.TOOL_NAME: action.tool,
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

    def set_default_agent(self, agent: Agent):
        self.agent = agent

    def get_default_agent(self, throw_if_missing: bool = True) -> Optional[Agent]:
        """Return the default agent of this agent service.

        This is a helper wrapper to safeguard naming conventions that have formed.
        """
        if hasattr(self, "agent"):
            return self.agent
        elif hasattr(self, "_agent"):
            return self._agent
        else:
            if throw_if_missing:
                raise SteamshipError(
                    message="No Agent object found in the Agent Service. "
                    "Please name it either self.agent or self._agent."
                )
            else:
                return None

    def build_default_context(self, context_id: Optional[str] = None, **kwargs) -> AgentContext:
        """Build's the agent's default context.

        The provides a single place to implement (or override) the default context that will be used by endpoints
        that transports define. This allows an Agent developer to use, eg, the TelegramTransport but with a custom
        type of memory or caching.

        The returned context does not have any emit functions yet registered to it.
        """

        # AgentContexts serve to allow the AgentService to run agents
        # with appropriate information about the desired tasking.
        if context_id is None:
            context_id = uuid.uuid4()
            logging.warning(
                f"No context_id was provided; generated {context_id}. This likely means no conversational history will be present."
            )

        use_llm_cache = self.use_llm_cache
        if runtime_use_llm_cache := kwargs.get("use_llm_cache"):
            use_llm_cache = runtime_use_llm_cache

        use_action_cache = self.use_action_cache
        if runtime_use_action_cache := kwargs.get("use_action_cache"):
            use_action_cache = runtime_use_action_cache

        context = AgentContext.get_or_create(
            client=self.client,
            context_keys={"id": f"{context_id}"},
            use_llm_cache=use_llm_cache,
            use_action_cache=use_action_cache,
        )

        # Add a default LLM to the context, using the Agent's if it exists.
        llm = None
        if agent := self.get_default_agent():
            if hasattr(agent, "llm"):
                llm = agent.llm
        if llm is None:
            llm = OpenAI(client=self.client)

        context = with_llm(context=context, llm=llm)

        return context

    @post("prompt")
    def prompt(
        self, prompt: Optional[str] = None, context_id: Optional[str] = None, **kwargs
    ) -> List[Block]:
        """Run an agent with the provided text as the input."""
        prompt = prompt or kwargs.get("question")

        context = self.build_default_context(context_id, **kwargs)

        context.chat_history.append_user_message(prompt)

        # Add a default LLM
        context = with_llm(context=context, llm=ChatOpenAI(client=self.client, model_name="gpt-4"))

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
        agent: Optional[Agent] = self.get_default_agent()
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
