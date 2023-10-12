from steamship import Steamship


def use_llama2_70b(text: str, client: Steamship) -> str:
    """LLama2 provides text generation."""
    llama2 = client.use_plugin(
        plugin_handle="replicate-llm",
        config={
            "model_name": "replicate/llama-2-70b-chat",  # Optional
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


# NOTE: In internal testing, replicate/llama-2-70b-chat consistently failed to return responses.
#
# @pytest.mark.usefixtures("client")
# def test_use_llama2(client: Steamship):
#     response = use_llama2_70b("Knock Knock!", client)
#     assert response
#     print(f"The 70B response is: {response}")
