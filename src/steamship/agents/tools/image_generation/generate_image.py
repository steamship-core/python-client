"""Tool for generating images."""

from steamship.agents.agent_context import DebugAgentContext
from steamship.agents.debugging import tool_repl
from steamship.agents.tools.tool import ImageGeneratorTool


class GenerateImageTool(ImageGeneratorTool):
    """Tool to generate images from text."""

    name: str = "GenerateImageTool"
    human_description: str = "Generates an image from text."
    ai_description = (
        "Used to generate images from text prompts. Only use if the user has asked directly for an "
        "image. When using this tool, the input should be a plain text string that describes, "
        "in detail, the desired image."
    )
    generator_plugin_handle: str = "dall-e"
    generator_plugin_config: dict = {"n": 1, "size": "256x256"}


def main():
    with DebugAgentContext.temporary() as context:
        tool = GenerateImageTool()
        tool_repl(tool, context)


if __name__ == "__main__":
    main()
