"""Tool for generating images."""
from steamship import Steamship
from steamship.agents.llms import OpenAI
from steamship.agents.tools import ImageGeneratorTool
from steamship.agents.utils import with_llm
from steamship.utils.repl import ToolREPL


class DalleTool(ImageGeneratorTool):
    """Tool to generate images from text using OpenAI's DALL-E."""

    name: str = "DalleTool"
    human_description: str = "Generates an image from text."
    agent_description = (
        "Used to generate still images from text prompts. Only use if the user has asked directly for an "
        "image. When using this tool, the input should be a plain text string that describes, "
        "in detail, the desired image."
    )
    generator_plugin_handle: str = "dall-e"
    generator_plugin_config: dict = {"n": 1, "size": "256x256"}


if __name__ == "__main__":
    tool = DalleTool()
    with Steamship.temporary_workspace() as client:
        ToolREPL(tool).run_with_client(client=client, context=with_llm(llm=OpenAI(client=client)))
