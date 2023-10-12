import pytest

from steamship import Steamship


def use_llama2_13b(text: str, client: Steamship) -> str:
    """LLama2 provides text generation."""
    llama2 = client.use_plugin(
        plugin_handle="replicate-llm",
        config={
            "model_name": "a16z-infra/llama-2-13b-chat",  # Optional
            "max_tokens": 256,  # Optional
            "temperature": 0.4,  # Optional
        },
    )

    task = llama2.generate(
        text=text,
        append_output_to_file=True,  # Persist the output so that it's stored for later
        make_output_public=True,  # Permit anyone to consume the output
    )

    task.wait()  # Wait for the generation to complete.

    output = task.output.blocks[0]  # Get the output block containing the response

    return output.text


@pytest.mark.usefixtures("client")
def test_use_llama2(client: Steamship):
    response = use_llama2_13b("Knock Knock!", client)
    assert response
    print(f"The 13B response is: {response}")
