Developing Blockifiers
~~~~~~~~~~~~~~~~~~~~~~

To develop a blockifier, first follow the instructions in _developing_plugins to create
a new plugin project. This will result in a full, working plugin scaffold that you could
deploy and use immediately.

Then, read below details about how to modify that scaffold for your own needs.

The Blockifier Contract
-----------------------

Blockifiers are responsible for transforming raw data into Steamship Block Format.
Using our SDK, that means implementing the following method:

.. code:: python

   class MyBlockifier(Blockifier):
       def run(self, request: PluginRequest[RawDataPluginInput]) -> Union[PluginRequest[BlockAndTagPluginOutput], BlockAndTagPluginOutput]:
           pass

A trivial implementation of this contract would be a pseudo-Markdown blockifier.
Let's say this blockifier assumes the input data is UTF-8, assumes that empty new lines represent paragraph breaks.
You could implement such a blockifier with this following code:

.. code:: python

   class PretendMarkdownBlockifier(Blockifier):
       def run(self, request: PluginRequest[RawDataPluginInput]) -> Union[PluginRequest[BlockAndTagPluginOutput], BlockAndTagPluginOutput]:
           # Grab the raw bytes.
           text = request.data.data

           # Decode it as UTF-8
           if isinstance(text, bytes):
               text = text.decode("utf-8")

          # Split it into paragraphs based on a double newline
          paragraphs = data.split("\n\n")

          # Create a block for each paragraph and add a tag marking it as a paragraph
          blocks = [
            Block.CreateRequest(text=paragraph, tags=[
                Tag.CreateRequest(kind="my-plugin", name="paragraph")
            ]) for paragraph in paragraphs
          ]

          # Return a BlockAndTagPluginOutput object
          return BlockAndTagPluginOutput(file=File.CreateRequest(blocks=blocks))

From the standpoint of the Steamship Engine, this ``PretendMarkdownBlockifier`` now provides a way to
transform any bytes claiming to be of this pseudo-markdown type into Steamship Block Format.

How to Structure Blocks and Tags
--------------------------------

The biggest design question you will likely face when implementing a blockifier is how to structure your blocks and tags.
At the platform level, we leave this open-ended on purpose, but we do encourage a few conventions of common convergence.

See the section Thinking in Blocks and Tags for more details.

Returning Errors
----------------

If something goes wrong during blockification, the preferred way to handle it is to raise an ``SteamshipError`` immediately.

.. code:: python

   raise SteamshipError(
      message="Detailed message",
      error=optional_nested_error_object)
   )

Asynchronous Blockifiers
------------------------

If your blockifier calls a third-party API that is asynchronous, then you should implement your
blockifier asynchronously as well.

The ``Request`` and ``Response`` objects passed into your blockifier's ``run`` function contain
fields which make this quick and easy. Here's how to do it.

First, let's imagine we have a third-party API that has three methods: one to start a long-running job,
one to check its status, and one to get the results.

.. code:: python

   class AsyncApi:
       def start_work(self) -> str
           return "job_id-1234"

       def is_complete(self) -> bool
           return False

       def get_result(self) -> bytes
           return b''

