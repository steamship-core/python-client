"""Tool for generating images."""
from steamship import Steamship
from steamship.agents.llms import OpenAI
from steamship.agents.tools import ImageGeneratorTool
from steamship.agents.utils import with_llm
from steamship.utils.repl import ToolREPL


class GoogleImageSearchTool(ImageGeneratorTool):
    """Tool to generate images from text by using Google Image Search."""

    name: str = "GoogleImageSearchTool"
    human_description: str = "Fetches an image from Google Image Search."
    agent_description = (
        "Used to retrieve an image of a well known object, person, place, or idea. Only use if the user has asked directly for an image. "
        "Input: a plain text string that describes an object, person, place, or idea. "
        "Output: an image of that thing."
    )
    generator_plugin_handle: str = "google-image-search"
    generator_plugin_config: dict = {}


if __name__ == "__main__":
    tool = GoogleImageSearchTool()
    with Steamship.temporary_workspace() as client:
        ToolREPL(tool).run_with_client(client=client, context=with_llm(llm=OpenAI(client=client)))
