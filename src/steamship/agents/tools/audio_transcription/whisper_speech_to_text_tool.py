"""Tool for generating images."""
from steamship.agents.tool import AudioBlockifierTool
from steamship.utils.repl import ToolREPL


class WhisperSpeechToTextTool(AudioBlockifierTool):
    """Tool to generate audio from text."""

    name: str = "WhisperSpeechToTextTool"
    human_description: str = "Generates text from spoken audio."
    ai_description: str = (
        "Used to generate text from spoken audio at a URL. Only use if the user has asked directly for a an text version of an audio file. "
        "The input is a URL. "
        "The output is the text from that URL."
    )
    blockifier_plugin_handle: str = "whisper-s2t-blockifier"


if __name__ == "__main__":
    print(
        "You can try: https://d3ctxlq1ktw2nl.cloudfront.net/staging/2023-4-14/2ba758be-d152-f80d-4ef0-9c63789e556b.mp3"
    )
    ToolREPL(WhisperSpeechToTextTool()).run()
    # Try on: https://anchor.fm/s/e1369b4c/podcast/play/70381739/https%3A%2F%2Fd3ctxlq1ktw2nl.cloudfront.net%2Fstaging%2F2023-4-14%2Fda96d64d-3c27-3e84-eb63-d5bc55eaf52e.mp3
