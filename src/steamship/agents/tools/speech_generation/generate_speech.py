"""Tool for generating images."""
from steamship import Steamship
from steamship.agents.llms import OpenAI
from steamship.agents.tools import AudioGeneratorTool
from steamship.agents.utils import with_llm
from steamship.utils.repl import ToolREPL


class GenerateSpeechTool(AudioGeneratorTool):
    """Tool to generate audio from text."""

    name: str = "GenerateSpokenAudio"
    human_description: str = "Generates spoken audio from text."
    agent_description: str = (
        "Used to generate spoken audio from text prompts. Only use if the user has asked directly for a "
        "an audio version of output. When using this tool, the input should be a plain text string containing the "
        "content to be spoken."
    )
    generator_plugin_handle: str = "elevenlabs"


if __name__ == "__main__":
    tool = GenerateSpeechTool()
    with Steamship.temporary_workspace() as client:
        ToolREPL(tool).run_with_client(client=client, context=with_llm(llm=OpenAI(client=client)))
