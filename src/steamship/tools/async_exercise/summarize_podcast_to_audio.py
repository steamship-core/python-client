from steamship.tools.audio_transcription.whisper_speech_to_text_tool import WhisperSpeechToTextTool
from steamship.tools.scheduling.map_concat_tool import MapConcatTool
from steamship.tools.scheduling.pipeline_tool import PipelineTool
from steamship.tools.speech_generation.generate_speech import GenerateSpeechTool
from steamship.tools.text_generation.summarize_text_with_prompt_tool import (
    SummarizeTextWithPromptTool,
)
from steamship.utils.repl import ToolREPL


class FetchAudioUrlsTool:
    pass


if __name__ == "__main__":
    entire_podcast_summarizer = PipelineTool(
        tools=[
            FetchAudioUrlsTool(),
            MapConcatTool(
                mapper=PipelineTool(
                    tools=[
                        WhisperSpeechToTextTool(),
                        SummarizeTextWithPromptTool(),
                    ]
                )
            ),
            GenerateSpeechTool(),
        ]
    )
    ToolREPL(entire_podcast_summarizer).run()


# https://d3ctxlq1ktw2nl.cloudfront.net/staging/2023-4-14/2ba758be-d152-f80d-4ef0-9c63789e556b.mp3
