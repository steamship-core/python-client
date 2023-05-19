# from steamship.tools.audio_transcription.whisper_speech_to_text_tool import WhisperSpeechToTextTool
# from steamship.tools.scheduling.tool_sequence import ToolSequence
# from steamship.tools.speech_generation.generate_speech import GenerateSpeechTool
# from steamship.tools.text_generation.summarize_text_with_prompt_tool import (
#     SummarizeTextWithPromptTool,
# )
# from steamship.utils.repl import ToolREPL
#
# if __name__ == "__main__":
#     summarize_audio = ToolSequence(
#         tools=[
#             WhisperSpeechToTextTool(),
#             SummarizeTextWithPromptTool(),
#             GenerateSpeechTool(),
#         ]
#     )
#
#     ToolREPL(summarize_audio).run()
#
# # https://d3ctxlq1ktw2nl.cloudfront.net/staging/2023-4-14/2ba758be-d152-f80d-4ef0-9c63789e556b.mp3
