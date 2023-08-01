.. _Dalle:

DALL-E
------

The DALL-E ``Generator`` plugin uses OpenAI's DALL-E to generate an image from a text description.

The plugin will combine all text that is passed to it into a single prompt for image generation. The plugin
handles retrying for rate limits and uses Steamship's OpenAI API key by default, eliminating the need
for you to have a separate OpenAI account.

The simplest possible example is:

.. code-block:: python

    dalle = steamship.use_plugin("dall-e")

    task = dalle.generate(text="A cat on a bicycle")
    task.wait()
    image_content = task.output.blocks[0].raw()

The :ref:`Generator <Generators>` interface supports many other ways to provide input and persist output.

The DALL-E plugin has a few :ref:`configuration parameters <Creating Plugin Instances>`:

- ``openai_api_key``: ``str``, An openAI API key to use. If left default, will use Steamship's API key.
- ``n``: ``numeric``, How many images to generate for each prompt.  This is how many ``Blocks`` will be in the output.
- ``size``: ``str``, default "1024x1024", The size of the ouptut images.  May be \"1024x1024\", \"512x512\", or \"256x256\".
- ``max_retries``: ``int``, default 8, Maximum number of retries to make when generating.
- ``request_timeout``: ``float``, default 600, maximum seconds to wait on calls to OpenAI.
