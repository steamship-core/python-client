import pytest

from steamship import Steamship


def use_dolly2_12b(text: str, client: Steamship) -> str:
    """Dolly2 provides text generation."""
    dolly2 = client.use_plugin(
        plugin_handle="replicate-llm",
        config={
            "model_name": "replicate/dolly-v2-12b",  # Optional
            "max_tokens": 256,  # Optional
            "temperature": 0.4,  # Optional
        },
    )

    task = dolly2.generate(
        text=text,
        append_output_to_file=True,  # Persist the output so that it's stored for later
        make_output_public=True,  # Permit anyone to consume the output
    )

    task.wait()  # Wait for the generation to complete.

    output = task.output.blocks[0]  # Get the output block containing the response

    return output.text


@pytest.mark.usefixtures("client")
def test_use_dolly2(client: Steamship):
    response = use_dolly2_12b("Knock Knock!", client)
    assert response
    print(f"The 12B response is: {response}")
