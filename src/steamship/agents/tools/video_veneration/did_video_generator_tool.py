"""Tool for generating images."""
from typing import List, Optional

from pydantic import BaseModel

from steamship.agents.tools import ImageGeneratorTool
from steamship.utils.repl import ToolREPL


class DIDVideoGeneratorOptions(BaseModel):
    DEFAULT_PROVIDER = {"type": "microsoft", "voice_id": "en-GB-AbbiNeural"}

    source_url: str
    """The URL of the source image to be animated."""

    stitch: str

    provider: Optional[dict]
    """Optional audio provider for generating the voice.

    Options:

    {"type": "microsoft", "voice_id": "en-GB-AbbiNeural"}
    {"type": "amazon", "voice_id": "Amy"}
    """

    driver_url: Optional[str]
    """The URL of the D-ID driver video. If not provided a driver video will be selected automatically."""

    expressions: Optional[List[dict]]
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


class DIDVideoGeneratorTool(ImageGeneratorTool):
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


if __name__ == "__main__":
    ToolREPL(DIDVideoGeneratorTool()).run()
