import pytest

from steamship import Steamship


def use_dalle(prompt: str, client: Steamship) -> str:
    """Use DALL-E from Python to generate an image whenever you need it."""
    sd = client.use_plugin(
        plugin_handle="dall-e",
        config={},
    )

    task = sd.generate(
        text=prompt,
        append_output_to_file=True,  # Persist the output so that it's stored for later
        make_output_public=True,  # Permit anyone to consume the output
    )

    task.wait()  # Wait for the generation to complete.

    output = task.output.blocks[0]  # Get the output block containing the image

    return output.raw_data_url


@pytest.mark.usefixtures("client")
def test_use_dalle(client: Steamship):
    image_url = use_dalle(
        "a cow standing in a field, majestic, 8k, award winning, best quality", client
    )
    assert image_url

    # WARNING: This workspace -- and the data within it -- will be deleted after the test runs by the `client` fixture.
    # If you are running this test in order to play the audio, set a breakpoint and play it.
    print(f"Your image is at: {image_url}")
