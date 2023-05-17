import logging
import uuid

from steamship import Block, Steamship
from steamship.agents.agent_context import DebugAgentContext
from steamship.agents.agents import Tool
from steamship.data.workspace import SignedUrl
from steamship.utils.signed_urls import upload_to_signed_url


class SteamshipREPL:
    client: Steamship

    def __init__(self):
        self.client = Steamship()

    def _make_image_public(self, block):
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


class ToolREPL(SteamshipREPL):
    tool: Tool

    def __init__(self, tool: Tool):
        super().__init__()
        self.tool = tool

    def print_block(self, block: Block):
        if isinstance(block, dict):
            block = Block.parse_obj(block)
        if block.is_text():
            print(block.text)
        elif block.url:
            print(block.url)
        elif block.content_url:
            print(block.content_url)
        else:
            url = self._make_image_public(block)
            print(url)

    def run(self):
        try:
            from termcolor import colored  # noqa: F401
        except ImportError:
            print("Error: Please run `pip install termcolor` to run this REPL.")
            exit(-1)

        with DebugAgentContext.temporary(client=self.client) as context:
            self.tool.register_in_context(context)

            print(f"Starting Tool {self.tool.name}...")
            print(
                "If you make code changes, you will need to restart this client. Press CTRL+C to exit at any time.\n"
            )

            while True:
                input_text = input(colored("Input: ", "blue"))  # noqa: F821
                input_block = Block(text=input_text)
                output_task = context.run_tool(self.tool.name, [input_block])
                for block in output_task.output:
                    self.print_block(block)
