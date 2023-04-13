.. _Files:

Files
~~~~~

Files are the top-level object for any piece of data in a workspace.

Files hold bytes of raw data (with a ``mime_type``, and processed data in :ref:`Blocks`.
A ``File`` may also have a list of :ref:`Tags` (annotations).

To do work on a ``File``, it needs to be saved and its content must be in :ref:`Blocks`.

There are a few ways to accomplish this:

- Create ``File`` and ``Block`` content directly (see below)
- Add raw data directly, then create ``Blocks`` with a :ref:`blockifier plugin<Blockifiers>`
- Import raw data with a :ref:`File Importer<File Importers>`, then create ``Blocks`` with a :ref:`blockifier plugin<Blockifiers>`

It's useful to think of Steamship Files more broadly than "file on your desktop."
They are any useful object:

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

