"""Tool for generating images."""
from typing import Any, List, Optional, Union

from steamship import Block, Task
from steamship.agents.schema import AgentContext
from steamship.agents.tools import VideoGeneratorTool
from steamship.utils.repl import ToolREPL

DEFAULT_SOURCE_URL = "https://steamship.com/images/agents/man-in-suit-midjournhey.jpg"


class DIDVideoGeneratorTool(VideoGeneratorTool):
    """Tool to generate talking avatars from text using D-ID."""

    name: str = "DIDVideoGeneratorTool"
    human_description: str = "Generates an a video of you speaking a response to a user."
    agent_description = (
        "Used to generate a video of you from text. Use if the user has asked for a video response.  "
        "The input is the text that you want to say. "
        "The output is the video of you saying it."
    )
    generator_plugin_handle: str = "did-video-generator"
    generator_plugin_config: dict = {}

    source_url: Optional[str] = DEFAULT_SOURCE_URL
    """The URL of the source image to be animated."""

    stitch: bool = True

    voice_provider: Optional[str] = "microsoft"
    """The voice provider. Must be either `microsoft` or `amazon`."""

    voice_id: Optional[str] = "en-US-GuyNeural"
    """The voice ID. E.g. `en-US-AshleyNeural` for Microsoft or `Amy` for Amazon."""

    driver_url: Optional[str] = None
    """The URL of the D-ID driver video. If not provided a driver video will be selected automatically."""

    expressions: Optional[List[dict]] = None
    """A list of expressions to apply.

    Valid expressions are: neutral | happy | surprise | serious
    Intensity is a float from 0 to 1.0

    Use the following form

    [
        {
            "start_frame": 0,
            "expression": "surprise",
            "intensity": 1.0
        },
    ]
    """

    transition_frames: Optional[int] = 20
    """How many frames to use for expression transition."""

    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Task[Any]]:
        """Run the tool. Copied from base class to enable generate-time config overrides."""

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
            task = generator.generate(
                text=prompt,
                make_output_public=True,
                append_output_to_file=True,
                options={
                    "source_url": self.source_url,
                    "stitch": self.stitch,
                    "provider": {
                        "type": self.voice_provider,
                        "voice_id": self.voice_id,
                        "voice_config": {"style": "Default"},
                        "expressions": self.expressions,
                    },
                    "transition_frames": self.transition_frames,
                },
            )
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


if __name__ == "__main__":
    ToolREPL(DIDVideoGeneratorTool()).run()
