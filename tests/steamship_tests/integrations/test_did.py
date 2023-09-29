from steamship import Steamship


def use_did(avatar_image_url: str, avatar_speech: str, client: Steamship) -> str:
    """Use Eleven Labs from Python to generate speech whenever you need it."""
    did = client.use_plugin(
        plugin_handle="did-video-generator",
    )

    # If you want to use D-ID to generate the voice, see:
    # https://learn.microsoft.com/en-us/azure/ai-services/speech-service/embedded-speech?tabs=android-target%2Cjre&pivots=programming-language-csharp
    options = {
        "source_url": avatar_image_url,
        "stitch": False,
        "provider": {
            "type": "microsoft",
            "voice_id": "en-US-GuyNeural",
            "voice_config": {"style": "Chat"},
        },
    }

    task = did.generate(
        text=avatar_speech,
        append_output_to_file=True,  # Persist the output so that it's stored for later
        make_output_public=True,  # Permit anyone to consume the output
        options=options,
    )

    task.wait()  # Wait for the generation to complete.

    output = task.output.blocks[0]  # Get the output block containing the audio

    return output.raw_data_url


# @pytest.mark.usefixtures("client")
# def test_use_elevenlabs(client: Steamship):
# ted_picture = "https://edwardbenson.com/images/ted-benson.jpg"
# ted_text = "Hardy har har!"

# Note: Because of the cost of D-ID, this test is left commented out.

# video_url = use_did(ted_picture, ted_text, client)
# assert video_url

# WARNING: This workspace -- and the data within it -- will be deleted after the test runs by the `client` fixture.
# If you are running this test in order to play the audio, set a breakpoint and play it.
# print(f"Your video is at: {video_url}")
