Thinking in Files, Blocks, and Tags
-----------------------------------

Steamship Plugins adapt other data formats and AI models into a common data model and operational model.
This means that, as a plugin author, you will need to make choices about how to perform that mapping.

Here are some tips for how to do that smoothly.

Files
~~~~~

We encourage you to think of Steamship's ``File`` object in a flexible light.
The following concepts could all fit nicely into what Steamship calls a ``File``:

- A PDF file you uploaded.
- A YouTube video.
- An AirTable table

Blocks
~~~~~~

We encourage you to think of Steamship's ``Block`` object as a necessary unit of data
paging, but otherwise completely free of meaning.
That it so say: it is useful to have some way to break a very large file into chunks
in order to optimnize processing and network traffic. But those chunks are considered
an implementation detail with respect to the contents of the file.

Consider a UTF-8 encoded CSV file uploaded to Steamship.
It should not matter whether this file is represented as:

- One block per row
- One block per 10 rows
- One block for the whole file

All semantic information about that file --- such as row and column boundaries --- should be
provided via tags atop the data, not blocks.

Tags
~~~~

We encourage you to think of Steamship's ``Tag`` object as typed key-values.
Using this framing:

- The ``kind`` field on a Tag represents its type
- The ``name`` field on a Tag represents its name
- The ``value`` field on a Tag is an optional JSON object representing its value

This results in an extraordinarily flexible data storage scheme that can be adapted to a number of
different scenarios.

Block Tags
~~~~~~~~~~

Tags located on blocks are called "Block Tags".
They do not annotate the blocks but rather the text within them.

Block Tags specifying a ``startIdx`` and ``endIdx`` which represent offsets into the text that is spanned by that block.
A blank ``startIdx`` is interpreted as the start of that text, and a blank ``endIdx`` is interpreted as the end of that text.

File Tags
~~~~~~~~~

Tags located on files are called "File Tags".

File tags are different than Block Tags in that they annotate the file itself, not the text within it.
The ``startIdx`` and ``endIdx`` fields must remain blank on a File Tag.

You can use a File Tag to store arbitrary information about a file that you wish to use in queries later,
such as source information, summaries, provenance, and so on.

