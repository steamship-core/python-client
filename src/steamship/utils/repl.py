import abc
import contextlib
import logging
import uuid
from abc import ABC
from typing import List, Optional, cast

from steamship import Block, Steamship, Task
from steamship.agents.context import AgentContext
from steamship.agents.tool import Tool
from steamship.data.workspace import SignedUrl, Workspace
from steamship.utils.signed_urls import upload_to_signed_url


class SteamshipREPL(ABC):
    """Base class for building REPLs that facilitate running Steamship code in the IDE."""

    client: Steamship

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

    def print_blocks(self, blocks: List[Block]):
        """Print a list of blocks to console."""
        for block in blocks:
            if isinstance(block, dict):
                block = Block.parse_obj(block)
            if block.is_text():
                print(block.text)
            elif block.url:
                print(block.url)
            elif block.content_url:
                print(block.content_url)
            else:
                url = self._make_public_url(block)
                print(url)

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

    def run_with_client(self, client: Workspace):
        try:
            from termcolor import colored  # noqa: F401
        except ImportError:

            def colored(message: str, color: str):
                print(message)

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
                self.print_blocks(blocks)

    def run(self):
        with self.temporary_workspace() as client:
            self.run_with_client(client)
