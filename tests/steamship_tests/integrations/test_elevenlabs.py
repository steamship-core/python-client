import pytest

from steamship import Steamship


def use_elevenlabs(text: str, client: Steamship) -> str:
    """Use Eleven Labs from Python to generate speech whenever you need it."""
    eleven = client.use_plugin(
        plugin_handle="elevenlabs",
        config={
            "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Optional
            "model_id": "eleven_monolingual_v1",  # Optional
            "stability": 0.5,  # Optional
            "similarity_boost": 0.8,  # Optional
        },
    )

    task = eleven.generate(
        text=text,
        append_output_to_file=True,  # Persist the output so that it's stored for later
        make_output_public=True,  # Permit anyone to consume the output
    )

    task.wait()  # Wait for the generation to complete.

    output = task.output.blocks[0]  # Get the output block containing the audio

    return output.raw_data_url


@pytest.mark.usefixtures("client")
def test_use_elevenlabs(client: Steamship):
    audio_url = use_elevenlabs("Hi there!", client)
    assert audio_url

    # WARNING: This workspace -- and the data within it -- will be deleted after the test runs by the `client` fixture.
    # If you are running this test in order to play the audio, set a breakpoint and play it.
    print(f"Your audio is at: {audio_url}")
