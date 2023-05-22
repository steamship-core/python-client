"""Tool for generating images."""
from steamship.agents.tool import ImageGeneratorTool
from steamship.utils.repl import ToolREPL


class GoogleImageSearchTool(ImageGeneratorTool):
    """Tool to generate images from text."""

    name: str = "GoogleImageSearchTool"
    human_description: str = "Fetches an image from Google Image Search."
    ai_description = (
        "Used to retrieve an image of a well known object, person, place, or idea. Only use if the user has asked directly for an image. "
        "Input: a plain text string that describes an object, person, place, or idea. "
        "Output: an image of that thing."
    )
    generator_plugin_handle: str = "google-image-search"
    generator_plugin_config: dict = {}


if __name__ == "__main__":
    ToolREPL(GoogleImageSearchTool()).run()
