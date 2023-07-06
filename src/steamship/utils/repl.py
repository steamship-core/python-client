import abc
import contextlib
import logging
import uuid
from abc import ABC
from typing import Any, Dict, List, Optional, Type, Union, cast

from steamship import Block, Steamship, SteamshipError, Task
from steamship.agents.llms import OpenAI
from steamship.agents.logging import AgentLogging
from steamship.agents.schema import Agent, AgentContext, Metadata, Tool
from steamship.agents.service.agent_service import AgentService
from steamship.agents.utils import with_llm
from steamship.data.workspace import Workspace
from steamship.invocable.dev_logging_handler import DevelopmentLoggingHandler

try:
    from termcolor import colored  # noqa: F401
except ImportError:

    def colored(text: str, **kwargs):
        print(text)


# Use either "gpt-3.5-turbo-0613" or "gpt-4-0613" here.
# Other versions of GPT tend not to work well with the ReAct prompt.
MODEL_NAME = "gpt-4-0613"


class SteamshipREPL(ABC):
    """Base class for building REPLs that facilitate running Steamship code in the IDE."""

    client: Steamship
    dev_logging_handler: DevelopmentLoggingHandler

    def __init__(self, log_level=None):
        logger = logging.getLogger()
        logger.handlers.clear()
        logger.setLevel(log_level or logging.DEBUG)
        dev_logging_handler = DevelopmentLoggingHandler()
        logger.addHandler(dev_logging_handler)

    def print_string(self, output: str, metadata: Optional[Dict[str, Any]] = None):
        """Print a string to console. All REPL output should ideally route through this method."""
        logging.info(
            f"{output}",
            extra={
                AgentLogging.IS_MESSAGE: True,
                AgentLogging.MESSAGE_AUTHOR: AgentLogging.AGENT,
                AgentLogging.MESSAGE_TYPE: AgentLogging.MESSAGE,
            },
        )

    def print_object(
        self, obj: Union[Task, Block, str, dict], metadata: Optional[Dict[str, Any]] = None
    ):
        """Print an object, returned by the agent or tool, to the console.

        Various epochs of the Agent SDK development have included Agents returning, to the repl: Blocks, strings, and
        Tasks. Since this is something that users can write (e.g. not controlled by the SDK) the REPL needs to handle
        all three cases in displaying output.
        """

        # A string gets printed wholesale.
        if isinstance(obj, str):
            self.print_string(obj, metadata)
            return

        # A task gets its ID printed.
        # TODO: It would be nice for this to be a link to the web UI.
        if isinstance(obj, Task):
            self.print_string(f"Task: {obj.task_id}", metadata)
            return

        # A dict is assumed to be a Block.
        if isinstance(obj, dict):
            obj = Block.parse_obj(obj)

        # A block gets handled based on what it contains.
        block = cast(Block, obj)
        if block.is_text():
            output = block.text
        elif block.url:
            output = block.url
        elif block.content_url:
            output = block.content_url
        else:
            block.set_public_data(True)
            output = block.raw_data_url
        if output:
            self.print_string(output, metadata)

    def print_object_or_objects(
        self, output: Union[List, Any], metadata: Optional[Dict[str, Any]] = None
    ):
        """Print Agent or Tool output, whether a list or a single object."""
        if isinstance(output, List):
            objects = cast(List, output)
            for obj in objects:
                self.print_object(obj, metadata)
        else:
            self.print_object(output, metadata)

    @contextlib.contextmanager
    def temporary_workspace(self) -> Steamship:
        workspace = Workspace.create(client=self.client)
        temp_client = Steamship(workspace=workspace.handle)
        yield temp_client
        workspace.delete()

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError()


class ToolREPL(SteamshipREPL):
    tool: Tool
    client = Steamship

    def __init__(self, tool: Tool, client: Optional[Steamship] = None):
        super().__init__()
        self.tool = tool
        self.client = client or Steamship()

    def run_with_client(self, client: Workspace, context: Optional[AgentContext] = None):
        if context is None:
            context = AgentContext()
        context.client = client

        print(f"Starting REPL for Tool {self.tool.name}...")
        print("If you make code changes, restart this REPL. Press CTRL+C to exit at any time.\n")

        while True:
            input_text = input(colored("Input: ", "blue"))  # noqa: F821
            input_block = Block(text=input_text)
            output = self.tool.run([input_block], context=context)
            self.print_object_or_objects(output)

    def run(self):
        with self.temporary_workspace() as client:
            self.run_with_client(client)


class AgentREPL(SteamshipREPL):
    agent_class: Type[AgentService]
    agent_instance: Optional[AgentService]
    client = Steamship
    config = None

    def __init__(
        self,
        agent_class: Type[AgentService],
        method: Optional[str] = None,
        agent_package_config: Optional[Dict[str, Any]] = None,
        client: Optional[Steamship] = None,
    ):
        super().__init__()
        self.agent_class = agent_class
        self.method = method
        self.client = client or Steamship()
        self.config = agent_package_config
        self.agent_instance = None

    def prompt(self, prompt: str, **kwargs) -> List[Block]:
        """Run an agent with the provided text as the input."""

        # AgentContexts serve to allow the AgentService to run agents
        # with appropriate information about the desired tasking.
        # Here, we create a new context on each prompt, and append the
        # prompt to the message history stored in the context.
        context_id = uuid.uuid4()
        context = AgentContext.get_or_create(self.client, {"id": f"{context_id}"})
        context.chat_history.append_user_message(prompt)

        # Add a default LLM
        context = with_llm(context=context, llm=OpenAI(client=self.client, model_name=MODEL_NAME))

        # AgentServices provide an emit function hook to access the output of running
        # agents and tools. The emit functions fire at after the supplied agent emits
        # a "FinishAction".
        #
        # Here, we show one way of accessing the output in a synchronous fashion. An
        # alternative way would be to access the final Action in the `context.completed_steps`
        # after the call to `run_agent()`.
        output = []

        def sync_emit(blocks: List[Block], meta: Metadata):
            nonlocal output
            output.extend(blocks)

        context.emit_funcs.append(sync_emit)

        if not self.agent_instance:
            raise SteamshipError(message="No agent_instance was found in the REPL.")

        # Get the agent
        agent_obj: Agent = None
        if hasattr(self.agent_instance, "agent"):
            agent_obj = self.agent_instance.agent
        elif hasattr(self.agent_instance, "_agent"):
            agent_obj = self.agent_instance._agent

        if not agent_obj:
            raise SteamshipError(
                message="No Agent object found in the Agent Service. "
                "Please name it either self.agent or self._agent."
            )

        self.agent_instance.run_agent(agent_obj, context)
        return output

    def run_with_client(self, client: Steamship, **kwargs):
        try:
            from termcolor import colored  # noqa: F401
        except ImportError:

            def colored(text: str, color: str):
                print(text)

        print("Starting REPL for Agent...")
        print("If you make code changes, restart this REPL. Press CTRL+C to exit at any time.\n")

        self.agent_instance = self.agent_class(client=client, config=self.config)

        # Determine the responder, which may have been custom-supplied on the agent.
        if self.method:
            responder = getattr(self.agent_instance, self.method)
        else:
            # No responder method was provided upon REPL bootup, so use the default
            # built-in to the REPL
            responder = self.prompt

        while True:
            input_text = input(colored(text="Input: ", color="blue"))  # noqa: F821
            output = responder(input_text)
            self.print_object_or_objects(output)

    def run(self, **kwargs):
        with self.temporary_workspace() as client:
            self.run_with_client(client, **kwargs)
