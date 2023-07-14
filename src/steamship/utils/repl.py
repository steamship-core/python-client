import abc
import contextlib
import logging
from abc import ABC
from json import JSONDecodeError
from typing import Any, Dict, List, Optional, Type, Union, cast

import requests

from steamship import Block, Steamship, Task, TaskState
from steamship.agents.logging import AgentLogging
from steamship.agents.schema import AgentContext, Tool
from steamship.agents.service.agent_service import AgentService
from steamship.data.workspace import Workspace
from steamship.invocable.dev_logging_handler import DevelopmentLoggingHandler

try:
    from termcolor import colored  # noqa: F401
except ImportError:

    def colored(text: str, **kwargs):
        print(text)


class SteamshipREPL(ABC):
    """Base class for building REPLs that facilitate running Steamship code in the IDE."""

    client: Steamship
    dev_logging_handler: DevelopmentLoggingHandler

    def __init__(
        self,
        log_level=None,
        dev_logging_handler=None,
    ):
        if not dev_logging_handler:
            self.dev_logging_handler = DevelopmentLoggingHandler.init_and_take_root()
        else:
            self.dev_logging_handler = dev_logging_handler

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

    def __init__(self, tool: Tool, client: Optional[Steamship] = None, **kwargs):
        super().__init__(**kwargs)
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
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.agent_class = agent_class
        self.method = method
        self.client = client or Steamship()
        self.config = agent_package_config
        self.agent_instance = None

    def run_with_client(self, client: Steamship, **kwargs):
        try:
            from termcolor import colored  # noqa: F401
        except ImportError:

            def colored(text: str, color: str, **kwargs):
                print(text)

        print("Starting REPL for Agent...")
        print("If you make code changes, restart this REPL. Press CTRL+C to exit at any time.\n")

        self.agent_instance = self.agent_class(client=client, config=self.config)

        # Determine the responder, which may have been custom-supplied on the agent.
        responder = getattr(self.agent_instance, self.method or "prompt")

        while True:
            input_text = input(colored(text="Input: ", color="blue"))  # noqa: F821
            output = responder(input_text)
            self.print_object_or_objects(output)

    def run(self, **kwargs):
        with self.temporary_workspace() as client:
            self.run_with_client(client, **kwargs)


class HttpREPL(SteamshipREPL):
    """REPL that uses an HTTP endpoint. Best for the `ship serve` command."""

    prompt_url: Optional[AgentService]
    client = Steamship
    config = None

    def __init__(self, prompt_url: str, client: Optional[Steamship] = None, **kwargs):
        super().__init__(**kwargs)
        self.prompt_url = prompt_url
        self.client = client or Steamship()

    def run_with_client(self, client: Steamship, **kwargs):  # noqa: C901
        try:
            from termcolor import colored  # noqa: F401
        except ImportError:

            def colored(text: str, color: str):
                print(text)

        print("Starting REPL for Agent...")
        print("If you make code changes, restart this REPL. Press CTRL+C to exit at any time.\n")
        while True:
            input_text = input(colored(text="Input: ", color="blue"))  # noqa: F821
            resp = requests.post(
                self.prompt_url,
                json={"prompt": input_text},
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.client.config.api_key.get_secret_value()}",
                },
            )

            result = None

            if not resp.ok:
                logging.error(
                    f"Request to AgentService failed with HTTP Status {resp.status_code}."
                )
                logging.error(f"Message: {resp.text}")
            try:
                result = resp.json()
            except JSONDecodeError as ex:
                logging.exception(ex)
            except BaseException as ex:
                logging.exception(ex)

            if result:
                if result.get("status", {}).get("state", None) == TaskState.failed:
                    message = result.get("status", {}).get("status_message", None)
                    logging.error(f"Response failed with remote error: {message or 'No message'}")
                    if suggestion := result.get("status", {}).get("status_suggestion", None):
                        logging.error(f"Suggestion: {suggestion}")
                elif data := result.get("data", None):
                    self.print_object_or_objects(data)
                else:
                    logging.warning(
                        "REPL interaction completed with empty data field in InvocableResponse."
                    )
            else:
                logging.warning("REPL interaction completed with no result to print.")

    def run(self, **kwargs):
        with self.temporary_workspace() as client:
            self.run_with_client(client, **kwargs)
