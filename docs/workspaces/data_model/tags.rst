.. _Tags:

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
^^^^^^^^^^

Tags located on blocks are called "Block Tags".
They do not annotate the blocks but rather the text within them.

Block Tags specifying a ``startIdx`` and ``endIdx`` which represent offsets into the text that is spanned by that block.
A blank ``startIdx`` is interpreted as the start of that text, and a blank ``endIdx`` is interpreted as the end of that text.

File Tags
^^^^^^^^^

Tags located on files are called "File Tags".

File tags are different than Block Tags in that they annotate the file itself, not the text within it.
The ``startIdx`` and ``endIdx`` fields must remain blank on a File Tag.

You can use a File Tag to store arbitrary information about a file that you wish to use in queries later,
such as source information, summaries, provenance, and so on.

