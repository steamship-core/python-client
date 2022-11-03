.. _Tags:

Tags
~~~~

Steamship uses Tags to represent all commentary about text.

- The intent of a chat message
- The embedding of a sentence
- The sentiment of a phase
- THe markdown semantics of a region of text

Steamship Files and Blocks are mostly semantics-free containers.
Tags are where all the action is.

The full :py:class:`Tag PyDoc spec is here<steamship.data.tags.tag.Tag>`, but it's useful to look at a summarized version:

.. code-block:: python

   class Tag:
     """Subset of the Tag object -- within the context of a Block"""

     # What the tag is
     kind:  str
     name:  Optional[str]
     value: Optional[Dict]

     # The span of text the tag is commenting upon.
     # Indices are relative to the block's text.
     start_idx: Optional[int]
     end_idx: Optional[int]

This design results in an extraordinarily flexible data storage scheme that can be adapted to a number of
different scenarios.
In the Engine, we optimize our data storage so that you can query over tags and their contents.

Ways to us Tags
^^^^^^^^^^^^^^^

Here are a few examples to help you think of how tags are used.
The ``start_idx`` and ``end_idx`` have been left out of the pseudo-code below.

- An entity

  .. code-block:: python

     Tag(kind="entity", name="person", value={"canonical": "Donald Duck"})

- A part of speech

  .. code-block:: python

     Tag(kind="part-of-speech", name="adj"})

- An embedding

  .. code-block:: python

     Tag(kind="embedding", name="my-embedder", value: {
       "vector-value": [0, 0, 0, 1, 0 .. 0]
     })

- A summary

  .. code-block:: python

     Tag(kind="generation", name="summary", value: {
       "text-value": "In which we show how to use tags"
     })

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

