"""Tool for generating images."""
from steamship.agents.debugging import ToolREPL
from steamship.tools.tool import AudioBlockifierTool


class WhisperSpeechToTextTool(AudioBlockifierTool):
    """Tool to generate audio from text."""

    name: str = "WhisperSpeechToTextTool"
    human_description: str = "Generates text from spoken audio."
    ai_description: str = (
        "Used to generate text from spoken audio. Only use if the user has asked directly for a "
        "an text version of an audio file. When using this tool, the input should be the audio file. "
        "The output is the text"
    )
    generator_plugin_handle: str = "whisper-s2t-blockifier"


if __name__ == "__main__":
    ToolREPL(WhisperSpeechToTextTool()).run()
