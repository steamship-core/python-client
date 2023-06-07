"""Tool for generating images."""
from typing import List, Optional

from pydantic import BaseModel

from steamship.agents.tools import ImageGeneratorTool
from steamship.utils.repl import ToolREPL


class DIDVideoGeneratorOptions(BaseModel):
    source_url: str
    """The URL of the source image to be animated."""

    stitch: str

    provider: Optional[str]
    """The URL of the D-ID driver video. If not provided a driver video will be selected automatically."""

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

    transition_frames: str


class DIDVideoGeneratorTool(ImageGeneratorTool):
    """Tool to generate talking avatars from text using D-ID."""

    name: str = "DIDVideoGeneratorTool"
    human_description: str = "Generates an a video of a talking avatar from text."
    agent_description = (
        "Used to generate a video of a talking avatar from text. Only use if the user has asked directly for an image. "
        "When using this tool, the input should be a plain text string that describes, "
        "in detail, the desired image."
    )
    generator_plugin_handle: str = "stable-diffusion"
    generator_plugin_config: dict = {"n": 1}


if __name__ == "__main__":
    ToolREPL(DIDVideoGeneratorTool()).run()
