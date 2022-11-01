.. _DevelopingBlockifiersSec:

Developing Blockifiers
----------------------

To develop a blockifier, first follow the instructions in :ref:`Developing Plugins<DevelopingPluginsSec>` to create
a new plugin project. This will result in a full, working plugin scaffold that you could
deploy and use immediately.

Then, read below details about how to modify that scaffold for your own needs.

The Blockifier Contract
~~~~~~~~~~~~~~~~~~~~~~~

Blockifiers are responsible for transforming raw data into Steamship Block Format.
Using our SDK, that means implementing the following method:

.. code-block:: python

   class MyBlockifier(Blockifier):
       def run(
          self, request: PluginRequest[RawDataPluginInput]
       ) -> Union[
          Response,
          Response[BlockAndTagPluginOutput]
       ]:
           pass

How to Structure Blocks and Tags
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The biggest design question you will face when implementing a blockifier is how to structure your blocks and tags.

At the platform level, we leave this open-ended on purpose, but we do encourage a few conventions of common convergence.

See the :ref:`Data Model` section for a discussion of how to think effectively about blocks and tags.

Synchronous Example: A Pseudo-Markdown Blockifier
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A trivial implementation of this contract would be a pseudo-Markdown blockifier.

Let's say this blockifier assumes the input data is UTF-8, assumes that empty new lines represent paragraph breaks.
You could implement such a blockifier with this following code:

.. code-block:: python

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

Asynchronous Blockifiers
~~~~~~~~~~~~~~~~~~~~~~~~

Some blockifiers will need to call third-party APIs that are asynchronous.
Image-to-text (OCR) and speech-to-text (S2T) are two common examples.
When this occurs, you should make your blockifier asynchronous as well.

See the :ref:`Developing Asynchronous Plugins<DevelopingAsync>` section for details.
