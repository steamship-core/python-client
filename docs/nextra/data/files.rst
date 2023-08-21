.. _Files:

Files
~~~~~

Files are the top-level object for any piece of data in a workspace.

A ``File`` contains the following:

* Raw source data, as bytes
* A ``mime_type``
* A list of :ref:`Blocks`, which represent the Steamship interpretation of the File's bytes
* A list of :ref:`Tags` (annotations), which provide key-value metadata about the file

To do work on a ``File``, its binary content needs to be converted into :ref:`Blocks`.

There are a few ways to accomplish this:

- Create ``File`` and ``Block`` content directly (see below)
- Create a ``File`` by uploading raw binary data, then convert it to ``Blocks`` with a :ref:`blockifier plugin<Blockifiers>`
- Create a ``File`` by importing raw binary data via a :ref:`File Importer<File Importers>`, then convert it to ``Blocks`` with a :ref:`blockifier plugin<Blockifiers>`

It's useful to think of Steamship Files more broadly than "file on your desktop."
The following are all comfortably modeled with a File object:

- A conversation between a user and an assistant
- a PDF file
- a YouTube video
- a Podcast episode
- A Notion page
- the JSON representation of an AirTable API response

Read the :py:class:`File PyDoc spec here<steamship.data.file.File>`.

.. _Creating Files Directly:

Creating Files Directly
-----------------------

The quickest way to create data is to create Files with ``Block`` content directly:

.. code-block:: python

   file = File.create(
      client=client,
      blocks=[Block(text="Some example text")]
   )

.. _Public Files:

Making File Data Public
------------------------

If you want the raw data bytes of a ``File`` to be publicly accessible, you can set the parameter ``public_data = True`` when calling ``File.create()``.
This is useful if you wish to share a generated image or audio file, or must make the content viewable in a place that cannot
retain your Steamship API key.  You can also change the value of the ``public_data`` flag on an existing ``File`` by calling
``File.set_public_data``.

Streaming Files
---------------

Updates to a File be consumed via a ``FileStream``.

* At the HTTP Level, this is implemented as Server-Sent Events (SSE)
* At the Python SDK and Typescript SDK levels, this is implemented in callbacks about file updates.



File streams contain the following events:

* ``block-created`` -
* ``block-deleted``

