import json
from abc import abstractmethod
from typing import Any, List, Optional, Union

import requests

from steamship import Block, File, MimeTypes, Task
from steamship.agents.schema import AgentContext, Tool


class GeneratorTool(Tool):
    """
    A base class for tools that wrap Steamship Generator plugins. Subclass this and implement
    the `accept_output_block` method.
    """

    generator_plugin_handle: str
    generator_plugin_instance_handle: Optional[str] = None
    generator_plugin_config: dict = {}
    merge_blocks: bool = False

    @abstractmethod
    def accept_output_block(self, block: Block) -> bool:
        raise NotImplementedError()

    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Task[Any]]:
        generator = context.client.use_plugin(
            plugin_handle=self.generator_plugin_handle,
            instance_handle=self.generator_plugin_instance_handle,
            config=self.generator_plugin_config,
        )

        tasks = []

        if self.merge_blocks:
            block = tool_input[0]
            for extra_block in tool_input[1:]:
                block.text = f"{block.text}\n\n{extra_block.text}"
            tool_input = [block]

        for block in tool_input:
            if isinstance(block, str):
                print(block)
            if not block.is_text():
                continue

            prompt = block.text
            task = generator.generate(text=prompt, append_output_to_file=True)
            tasks.append(task)

        # TODO / REMOVE Synchronous execution is a temporary simplification while we merge code.
        output_blocks = []
        # NB: In an async framework, we need to contend with the fact that we have some Monad-style trickery
        # to contend with. Namely that the below code has taken us from List[Block] as the universal type to
        # List[List[Block]] as the async result that we will have to process.
        #
        # It's unclear to me (ted) if this is something we leave as an exercise for implementors or build in
        # as universally handled.
        for task in tasks:
            task.wait()
            task_blocks = self.post_process(task, context)
            for block in task_blocks:
                output_blocks.append(block)
        # END TODO / REMOVE

        return output_blocks

    def post_process(self, task: Task, context: AgentContext) -> List[Block]:
        """In this case, the Generator returns a GeneratorResponse that has a .blocks method on it"""
        try:
            return task.output.blocks
        except BaseException:
            return json.loads(task.output).get("blocks")


class ImageGeneratorTool(GeneratorTool):
    """
    A base class for tools that wrap Steamship Image Generator plugins.
    """

    def accept_output_block(self, block: Block) -> bool:
        return block.is_image()


class VideoGeneratorTool(GeneratorTool):
    """
    A base class for tools that wrap Steamship Video Generator plugins.
    """

    def accept_output_block(self, block: Block) -> bool:
        return block.is_video()


class AudioGeneratorTool(GeneratorTool):
    """
    A base class for tools that wrap Steamship Audio Generator plugins.
    """

    def accept_output_block(self, block: Block) -> bool:
        return block.is_audio()


class ScrapeAndBlockifyTool(Tool):
    """
    A base class for tools that wrap Steamship Blockifier plugin which transforms bytes to a set of blocks.
    """

    blockifier_plugin_handle: str
    blockifier_plugin_instance_handle: Optional[str] = None
    blockifier_plugin_config: dict = {}

    @abstractmethod
    def should_blockify(self, block: Block) -> bool:
        raise NotImplementedError()

    def get_mime_type(self):
        return None

    def _scrape(self, url: str, context: AgentContext) -> File:
        response = requests.get(url)
        file = File.create(context.client, content=response.content, mime_type=self.get_mime_type())
        return file

    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Task[Any]]:
        tasks = []

        blockifier = context.client.use_plugin(
            plugin_handle=self.blockifier_plugin_handle,
            instance_handle=self.blockifier_plugin_instance_handle,
            config=self.blockifier_plugin_config,
        )

        for input_block in tool_input:
            if not input_block.is_text():
                continue

            url = input_block.text
            file = self._scrape(url, context)
            task = file.blockify(blockifier.handle)
            tasks.append(task)

        # TODO / REMOVE Synchronous execution is a temporary simplification while we merge code.
        output_blocks = []
        # NB: In an async framework, we need to contend with the fact that we have some Monad-style trickery
        # to contend with. Namely that the below code has taken us from List[Block] as the universal type to
        # List[List[Block]] as the async result that we will have to process.
        #
        # It's unclear to me (ted) if this is something we leave as an exercise for implementors or build in
        # as universally handled.
        for task in tasks:
            task.wait()
            task_blocks = self.post_process(task, context)
            for block in task_blocks:
                output_blocks.append(block)
        # END TODO / REMOVE

        return output_blocks

    def post_process(self, task: Task, context: AgentContext) -> List[Block]:
        """In this case, the Blockifier returns a BlockAndTagResponse that has a .file.blocks method on it"""
        try:
            return task.output.file.blocks
        except BaseException:
            return json.loads(task.output).get("file", {}).get("blocks")


class ImageBlockifierTool(ScrapeAndBlockifyTool):
    """
    A base class for tools that wrap Steamship Image Blockifier plugins.
    """

    def get_mime_type(self):
        return MimeTypes.PNG

    def should_blockify(self, block: Block) -> bool:
        return block.is_image()


class AudioBlockifierTool(ScrapeAndBlockifyTool):
    """
    A base class for tools that wrap Steamship Audio Blockifier plugins.
    """

    def get_mime_type(self):
        return MimeTypes.MP3

    def should_blockify(self, block: Block) -> bool:
        return block.is_audio()
