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
     start_idx: Optional[int] # Start inclusive
     end_idx: Optional[int]   # End exclusive

This design results in an extraordinarily flexible data storage scheme that can be adapted to a number of
different scenarios.
In the Engine, we optimize our data storage so that you can query over tags and their contents.

Ways to use Tags
^^^^^^^^^^^^^^^^

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

- A summarization

  .. code-block:: python

     Tag(kind="generation", name="summary", value: {
       "string-value": "... summary of the span covered by this tag ..."
     })

- A dictionary lookup

  .. code-block:: python

     Tag(kind="token", name="ce-dict", value: {
       "chinese": "你好", "pinyin": "nǐhǎo", "english": "hello"
     })

Tag Schemas
^^^^^^^^^^^

Steamship brings together many models under one roof using tags as the common representation for interoperation.
But doesn't fully solve the model interop problem: how do we make sure all models use the same tags?

Our answer to this is to converge -- where possible -- upon a common schema for the ``kind``, ``name``, and ``value`` properties of a tag.
If all sentiment models emit a tag with kind ``sentiment`` and a range of names ``[positive, neutral, negative]``, for example, then we can swap them in and out as it suits us.

Our ongoing pursuit of this can be found in the `tag_constants.py file <https://github.com/steamship-core/python-client/blob/main/src/steamship/data/tags/tag_constants.py>`_
in Github.
There you will find Python Enum classes that we curate as we encounter common domains across our plugins.

- :py:class:`TagKind class<steamship.data.tags.tag_constants.TagKind>` contains suggested values for the ``kind`` field of a Tag.
- :py:class:`TagValue class<steamship.data.tags.tag_constants.TagValue>` contains suggested keys for the ``valu`` dictionary of a Tag.
- The following classes contain suggested values for the ``name`` field:

  - :py:class:`DocTag<steamship.data.tags.tag_constants.DocTag>` for document semantics (HTML, Markdown, OCR, etc)
  - :py:class:`EmotionTag<steamship.data.tags.tag_constants.EmotionTag>` for emotion tagging tag
  - :py:class:`EntityTag<steamship.data.tags.tag_constants.EntityTag>` for entity tagging tags
  - :py:class:`GenerationTag<steamship.data.tags.tag_constants.GenerationTag>` for models which generate new data from the covered span as input
  - :py:class:`IntentTag<steamship.data.tags.tag_constants.IntentTag>` for intent classification
  - :py:class:`SentimentTag<steamship.data.tags.tag_constants.SentimentTag>` for sentiment classification

These constants are by no means required, but using them increases the chance that what you build will
interoperate cleanly with everyone else that uses them.

Here is what some of the above tag examples would look like using these enum classes.
Notice how it is a combination of standard constant and "magic string" depending on whether a constant exists for that concept.

- An entity

  .. code-block:: python

     from steamship.data import TagKind, EntityTag
     Tag(kind=TagKind.ENTITY, name=EntityTag.PERSON, value={"canonical": "Donald Duck"})

- A part of speech

  .. code-block:: python

     from steamship.data import TagKind
     Tag(kind=TagKind.PART_OF_SPEECH, name="adj"})

- An embedding

  .. code-block:: python

     from steamship.data import TagKind, TagValue
     Tag(kind=TagKind.EMBEDDING, name="my-embedder", value: {
       TagValue.VECTOR_VALUE: [0, 0, 0, 1, 0 .. 0]
     })

- A summarization

  .. code-block:: python

     from steamship.data import TagKind, GenerationTag, TagValue
     Tag(kind=TagKind.GENERATION, name=GenerationTag.SUMMARY, value: {
       TagValue.STRING_VALUE: "... summary of the span covered by this tag ..."
     })

- A dictionary lookup

  .. code-block:: python

     from steamship.data import TagKind
     Tag(kind=TagKind.TOKEN, name="ce-dict", value: {
       "chinese": "你好", "pinyin": "nǐhǎo", "english": "hello"
     })


Block and File Tags
^^^^^^^^^^^^^^^^^^^

The above text discusses tags upon spans of text.
But Steamship actually supports two types of tags: **File Tags** and **Block Tags**.

**File Tags** annotate a :ref:`File<Files>` object itself:

- They are attached to the :ref:`File<Files>` object (``file.tags``)
- Their ``block_id``, ``start_idx``, and ``end_idx`` are always null.
- They are referenced via the ``filetag`` keyword in our query system.

**Block Tags** annotate text within a :ref:`Block<Blocks>` object:

- They are attached to the :ref:`Block<Blocks>` object (``block.tags``)
- Their ``start_idx`` and ``end_idx`` fields are non-null. They  represent offsets into the text that is spanned by that block.
- They are referenced via the ``blocktag`` keyword in our query system.

There are a few edge cases important to call out here:

- Whereas file tags annotate the file itself, block tags do not annotate the block: they annotate text within the block.
- A block tag that covers the entire text of the block always has ``start_idx = 0`` and ``end_idx = len(block.text)``
- It is impossible for a tag to cover text spanning multiple blocks. This is a limitation of our current data model.
