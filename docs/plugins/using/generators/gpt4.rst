.. _gpt4:

GPT-4 (and GPT 3.5)
------

The GPT-4 ``Generator`` plugin uses OpenAI's GPT-4 to generate text from a text prompt,
or the continuation of a chat. It can also be used with GPT-3.5 by passing ``"gpt-3.5-turbo"``
as the ``model`` configuration parameter.

The plugin will treat each ``Block`` of the input as an element of a chat. If a ``Block`` has
a ``Tag`` of kind "role" and name ( "system" | "user" | "assistant" ), the content will be passed
to OpenAI with the corresponding role. If a ``Block`` does not have a role tag, it will
be passed with the configured default role, which defaults to "user" (see config params below).

The plugin handles retrying for rate limits and uses Steamship's OpenAI API key by default,
eliminating the need for you to have a separate OpenAI account.

The simplest possible example is:

.. code-block:: python

    gpt4 = steamship.use_plugin("gpt-4")

    task = gpt4.generate(text="Tell me a joke")
    task.wait()
    joke = task.output.blocks[0].text

To build a chat interaction, you can persist the prompt components to a ``File`` object,
tagging them with their conversational roles:

.. code-block:: python

    gpt4 = steamship.use_plugin("gpt-4")

    chat_file = File.create(client, blocks=[
        Block(
            text="You are an assistant who likes to tell jokes about bananas",
            tags=[Tag(kind=TagKind.ROLE, name=RoleTag.SYSTEM)]
        )
    ])
    chat_file.append_block(
        text="Do you know any fruit jokes?",
        tags=[Tag(kind=TagKind.ROLE, name=RoleTag.USER)]
    )
    task = gpt4.generate(
        input_file_id=chat_file.id,
        append_output_to_file=True,
        output_file_id=chat_file.id
    )
    task.wait()
    joke = task.output.blocks[0].text

In the example above, in addition to being returned as the result of the ``Task``, the output
``Block`` is appended to ``chat_file``.

All output ``Blocks`` will be tagged with the "assistant" role to allow more
content to be easily appended and generated.

The :ref:`Generator <Generators>` interface supports many other ways to provide input and persist output.

The GPT-4 plugin has a few :ref:`configuration parameters <Creating Plugin Instances>`:

- ``openai_api_key``: ``str``, An openAI API key to use. If left default, will use Steamship's API key.
- ``max_tokens``: ``int``, default 256, The maximum number of tokens to generate per request. Can be overridden in runtime options.
- ``model``: ``str`` , default "gpt-4", The OpenAI model to use. Can be a pre-existing fine-tuned model.
- ``temperature``: ``float`` , default 0.4, Controls randomness. Lower values produce higher likelihood / more predictable results; higher values produce more variety. Values between 0-1.
- ``top_p``: ``int``, default 1, Controls the nucleus sampling, where the model considers the results of the tokens with top_p probability mass. Values between 0-1.
- ``presence_penalty``: ``int``, default 0, Control how likely the model will reuse words. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics. Number between -2.0 and 2.0.
- ``frequency_penalty``: ``int``, default 0, Control how likely the model will reuse words. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim. Number between -2.0 and 2.0.
- ``moderate_output``: ``bool`` , default True, Pass the generated output back through OpenAI's moderation endpoint and throw an exception if flagged.
- ``max_retries``: ``int`` , default 8, Maximum number of retries to make when generating.
- ``request_timeout``: ``float``, default 600, Timeout for requests to OpenAI completion API. Default is 600 seconds.
- ``n``: ``int``, default 1, How many completions to generate for each prompt.
- ``default_role``: ``str``, default RoleTag.USER, The default role to use for a block that does not have a Tag of kind='role'
- ``default_system_prompt``: ``str`` , default "", System prompt that will be prepended before every request


Additionally, stopwords can be passed in the ``stop`` parameter in the ``options`` of the
``generate`` call. Other parameters may be overridden on an individual invocation by passing
them in the ``options`` as well.

