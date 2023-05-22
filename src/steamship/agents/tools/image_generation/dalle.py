"""Tool for generating images."""
from steamship.agents.tool import ImageGeneratorTool
from steamship.utils.repl import ToolREPL


class DalleTool(ImageGeneratorTool):
    """Tool to generate images from text."""

    name: str = "DalleTool"
    human_description: str = "Generates an image from text."
    ai_description = (
        "Used to generate images from text prompts. Only use if the user has asked directly for an "
        "image. When using this tool, the input should be a plain text string that describes, "
        "in detail, the desired image."
    )
    generator_plugin_handle: str = "dall-e"
    generator_plugin_config: dict = {"n": 1, "size": "256x256"}


if __name__ == "__main__":
    ToolREPL(DalleTool()).run()
