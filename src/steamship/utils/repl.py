import abc
import contextlib
import logging
import uuid
from abc import ABC
from typing import Any, Dict, List, Optional, Type, cast

from steamship import Block, Steamship, Task
from steamship.agents.logging import AgentLogging
from steamship.agents.schema import AgentContext, Tool
from steamship.agents.service.agent_service import AgentService
from steamship.data.workspace import SignedUrl, Workspace
from steamship.invocable.dev_logging_handler import DevelopmentLoggingHandler
from steamship.utils.signed_urls import upload_to_signed_url


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

    def _make_public_url(self, block):
        filepath = str(uuid.uuid4())
        signed_url = (
            self.client.get_workspace()
            .create_signed_url(
                SignedUrl.Request(
                    bucket=SignedUrl.Bucket.PLUGIN_DATA,
                    filepath=filepath,
                    operation=SignedUrl.Operation.WRITE,
                )
            )
            .signed_url
        )
        logging.info(f"Got signed url for uploading block content: {signed_url}")
        read_signed_url = (
            self.client.get_workspace()
            .create_signed_url(
                SignedUrl.Request(
                    bucket=SignedUrl.Bucket.PLUGIN_DATA,
                    filepath=filepath,
                    operation=SignedUrl.Operation.READ,
                )
            )
            .signed_url
        )
        upload_to_signed_url(signed_url, block.raw())
        return read_signed_url

    def print_blocks(self, blocks: List[Block], metadata: Dict[str, Any]):
        """Print a list of blocks to console."""
        output = None

        for block in blocks:
            if isinstance(block, dict):
                block = Block.parse_obj(block)
            if block.is_text():
                output = block.text
            elif block.url:
                output = block.url
            elif block.content_url:
                output = block.content_url
            else:
                url = self._make_public_url(block)
                output = url

        if output:
            logging.info(
                f"{output}",
                extra={
                    AgentLogging.IS_MESSAGE: True,
                    AgentLogging.MESSAGE_AUTHOR: AgentLogging.AGENT,
                },
            )

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
        try:
            from termcolor import colored  # noqa: F401
        except ImportError:

            def colored(message: str, color: str):
                print(message)

        if context is None:
            context = AgentContext()
        context.client = client

        print(f"Starting REPL for Tool {self.tool.name}...")
        print("If you make code changes, restart this REPL. Press CTRL+C to exit at any time.\n")

        while True:
            input_text = input(colored("Input: ", "blue"))  # noqa: F821
            input_block = Block(text=input_text)
            output = self.tool.run([input_block], context=context)
            if isinstance(output, Task):
                # TODO: Iterate on task support.
                print(f"Task: {output.task_id}")
            else:
                blocks = cast(List[Block], output)
                self.print_blocks(blocks, {})

    def run(self):
        with self.temporary_workspace() as client:
            self.run_with_client(client)


class AgentREPL(SteamshipREPL):
    agent_class: Type[AgentService]
    client = Steamship
    config = None

    def __init__(
        self,
        agent_class: Type[AgentService],
        method: str,
        agent_package_config: Optional[Dict[str, Any]],
        client: Optional[Steamship] = None,
    ):
        super().__init__()
        self.agent_class = agent_class
        self.method = method
        self.client = client or Steamship()
        self.config = agent_package_config

    def run_with_client(self, client: Steamship):
        try:
            from termcolor import colored  # noqa: F401
        except ImportError:

            def colored(text: str, color: str):
                print(text)

        print("Starting REPL for Agent...")
        print("If you make code changes, restart this REPL. Press CTRL+C to exit at any time.\n")

        agent_service = self.agent_class(client=client, config=self.config)

        while True:
            input_text = input(colored(text="Input: ", color="blue"))  # noqa: F821
            responder = getattr(agent_service, self.method)
            response = responder(input_text)
            print(colored(text=f"{response}", color="green", force_color=True))

    def run(self):
        with self.temporary_workspace() as client:
            self.run_with_client(client)
