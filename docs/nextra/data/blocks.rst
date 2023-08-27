.. _Blocks:

Blocks
~~~~~~

Blocks are ordered chunks of content within a :ref:`File <Files>`.

A :py:class:`Block<steamship.data.block.Block>` may have raw data, plain text, or both.  The type of content is indicated by its ``mime_type``.
Blocks can store images, videos, audio clips, or any other chunk of data.

This means that different packages and plugins may choose divide files into blocks using different schemes.
Consider a CSV file uploaded to Steamship.
The following divisions of this file into blocks are all perfectly fine:

- Each CSV row is a block of text.
- Each 10 CSV rows is a block
- The entire CSV file is one block

Metadata and annotations about the content of the :py:class:`Block<steamship.data.block.Block>` added via :ref:`Tags` on the :py:class:`Block<steamship.data.block.Block>` .

.. _Creating Blocks:

Creating Blocks
---------------

Blocks may be created when creating a :py:class:`File<steamship.data.file.File>` by passing them in the ``blocks`` parameter, or they can be appended
to an existing file.

Please see ``Block.create()`` and ``File.append_block()``.

Read the :py:class:`Block PyDoc spec here<steamship.data.block.Block>`.

.. _Public Blocks:

Making Block Data Public
------------------------

If you want the raw data bytes of a :py:class:`Block<steamship.data.block.Block>` to be publicly accessible, you can set the parameter ``public_data = True`` when calling ``Block.create()``.
This is useful if you wish to share a generated image or audio file, or must make the content viewable in a place that cannot
retain your Steamship API key.  You can also change the value of the ``public_data`` flag on an existing :py:class:`Block<steamship.data.block.Block>` by calling
``Block.set_public_data``.

Streaming Blocks
----------------

A :py:class:`Block<steamship.data.block.Block>`'s content is immutable once created, but during the creation of a block its contents can be streamed.

This stream consists of raw bytes, to be interpreted by the block's MIME Type.
