from steamship.tools.audio_transcription.fetch_audio_urls_from_rss_tool import (
    FetchAudioUrlsFromRssTool,
)
from steamship.tools.audio_transcription.whisper_speech_to_text_tool import WhisperSpeechToTextTool
from steamship.tools.scheduling.map_concat_tool import MapConcatTool
from steamship.tools.scheduling.pipeline_tool import PipelineTool
from steamship.tools.speech_generation.generate_speech import GenerateSpeechTool
from steamship.tools.text_generation.summarize_text_with_prompt_tool import (
    SummarizeTextWithPromptTool,
)
from steamship.utils.repl import ToolREPL

if __name__ == "__main__":
    entire_podcast_summarizer = PipelineTool(
        name="EntirePodcastSummarizer",
        tools=[
            FetchAudioUrlsFromRssTool(),
            MapConcatTool(
                mapper=PipelineTool(
                    name="SinglePodcastSummarizer",
                    tools=[
                        WhisperSpeechToTextTool(),
                        SummarizeTextWithPromptTool(),
                    ],
                )
            ),
            GenerateSpeechTool(),
        ],
    )

    # TODO: Nasty bug where registering the same tool twice causes it to overwrite unless you make custom name
    ToolREPL(entire_podcast_summarizer).run()


# https://anchor.fm/s/e1369b4c/podcast/rss
