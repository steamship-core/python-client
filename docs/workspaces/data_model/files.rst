Files
~~~~~

Files are the top-level object for any piece of data in a workspace.

Before Steamship can use it, a files is always:

- :ref:`Imported<Importing Data>` as raw data or imported via a plugin
- :ref:`Blockified<Blockifying Data>`, converting the raw data into :ref:`Blocks` and :ref:`Tags`

It's useful to think of Steamship Files more broadly than "file on your desktop."
They are any useful object that contains natural langauge:

- a PDF file
- a YouTube video
- a Podcast episode
- A Notion page
- the JSON representation of an AirTable API response

Read the :py:class:`File PyDoc spec here<steamship.data.file.File>`.
