"""Tool for generating images."""
from steamship.agents.tool import AudioBlockifierTool
from steamship.utils.repl import ToolREPL


class AssemblySpeechToTextTool(AudioBlockifierTool):
    """Tool to generate text from audio."""

    name: str = "AssemblySpeechToTextTool"
    human_description: str = "Generates text from spoken audio."
    ai_description: str = (
        "Used to generate text from spoken audio. Only use if the user has asked directly for a "
        "an text version of an audio file. When using this tool, the input should be the audio file. "
        "The output is the text"
    )
    blockifier_plugin_handle: str = "s2t-blockifier-assembly"


if __name__ == "__main__":
    ToolREPL(AssemblySpeechToTextTool()).run()
    # Try on: https://anchor.fm/s/e1369b4c/podcast/play/70381739/https%3A%2F%2Fd3ctxlq1ktw2nl.cloudfront.net%2Fstaging%2F2023-4-14%2Fda96d64d-3c27-3e84-eb63-d5bc55eaf52e.mp3
