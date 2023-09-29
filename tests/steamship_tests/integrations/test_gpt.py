import pytest

from steamship import Steamship


def use_gpt(text: str, client: Steamship) -> str:
    """GPT-4 provides text generation, code generation, and function-calling.

    Note: The plugin is called gpt-4 but it can call most GPT models based on its configuration. Billing will be
    applied appropriately based on the model you choose.

    See https://github.com/steamship-plugins/gpt4/blob/main/src/api.py for the full list of configuration params.
    """
    gpt = client.use_plugin(
        plugin_handle="gpt-4",
        config={
            "model": "gpt-4",  # Optional
            "max_tokens": 256,  # Optional
            "temperature": 0.4,  # Optional
        },
    )

    task = gpt.generate(
        text=text,
        append_output_to_file=True,  # Persist the output so that it's stored for later
        make_output_public=True,  # Permit anyone to consume the output
    )

    task.wait()  # Wait for the generation to complete.

    output = task.output.blocks[0]  # Get the output block containing the response

    return output.text


@pytest.mark.usefixtures("client")
def test_use_gpt(client: Steamship):
    response = use_gpt("Knock Knock!", client)
    assert response
    print(f"The response is: {response}")
