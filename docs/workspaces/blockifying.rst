.. _Blockifying Data:

Blockifying Data
----------------

Blockifying content transforms raw bytes (audio, text, markdown, HTML) into Steamship's :ref:`Block and Tag Format<Data Model>`
format. This is how Steamship creates a space for many different AI models to interoperate over the same data.

Steamship's plugin index maintains `a list of Blockifiers you can use <https://www.steamship.com/plugins/>`_.
Select the one appropriate for your data type and then apply it.

Here is how to blockify a Markdown file using the ``markdown-blockifier-default`` blockifier:

.. tab:: Python

    .. code-block:: python

       import { Steamship, MimeTypes } from "@steamship/client"
       client = Steamship()

       file = File.create(
          client=client,
          content="# This is a header \n\n And this is a paragraph!",
          mime_type=MimeTypes.MKD
       )

       blockifier = client.use_plugin("markdown-blockifier-default")
       task = file.blockify(blockifier.handle)
       task.wait()

Once Blockified, that file can be:

- Refreshed, to pull down its blocks and tags locally,
- Tagged, using tagger plugins, to add more information to it,
- Queried using our query system
