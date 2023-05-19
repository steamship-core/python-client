"""Tool for generating images."""
from steamship.tools.tool import AudioBlockifierTool
from steamship.utils.repl import ToolREPL


class WhisperAudioTranscriptionTool(AudioBlockifierTool):
    """Tool to generate text from audio."""

    name: str = "GenerateSpokenAudio"
    human_description: str = "Generates spoken audio from text."
    ai_description: str = (
        "Used to generate spoken audio from text prompts. Only use if the user has asked directly for a "
        "an audio version of output. When using this tool, the input should be a plain text string containing the "
        "content to be spoken."
    )
    generator_plugin_handle: str = "elevenlabs"


if __name__ == "__main__":
    ToolREPL(WhisperAudioTranscriptionTool()).run()
