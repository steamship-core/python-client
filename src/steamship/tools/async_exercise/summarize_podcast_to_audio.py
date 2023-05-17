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
    fetch_episodes = FetchAudioUrlsTool()
    create_file_of_summaries = MapConcatTool(
        mapper=PipelineTool(
            tools=[
                WhisperSpeechToTextTool(),
                SummarizeTextWithPromptTool(),
            ]
        )
    )
    generate_speech = GenerateSpeechTool()

    final_pipeline = PipelineTool(
        tools=[
            fetch_episodes,
            create_file_of_summaries,
            generate_speech,
        ]
    )

    ToolREPL(final_pipeline).run()


# https://d3ctxlq1ktw2nl.cloudfront.net/staging/2023-4-14/2ba758be-d152-f80d-4ef0-9c63789e556b.mp3
