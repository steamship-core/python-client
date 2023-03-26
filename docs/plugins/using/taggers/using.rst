Using Taggers
-------------

To use a tagger, create an instance within your workspace and then apply it to a file.
Note that a file must first have :ref:`Blocks`, either by direct creation or using a :ref:`Blockifier<Blockifiers>`.

.. code-block:: python

   from steamship import Steamship, File
   client = Steamship(workspace="my-workspace-handle")

   file = File.create(client, blocks=[Block(text="some text to tag")])

   # Create the tagger instance
   tagger = client.use_plugin('tagger-handle')

   # Apply the tagger to the file
   tagger_task = file.tag(tagger.handle)
   tagger_task.wait()

   # Refresh the file to see new tags
   file.refresh()

   # and/or Query across the persisted tags returned from tagging.
   file.query('blocktag AND name "paragraph"')



Input
-----

The input to a ``tag`` operation is a ``File``.  Most ``Taggers`` by default will tag all ``Blocks`` within that file.

Output
------

When you call ``tag`` on a file or via a ``PluginInstance``, the object that is returned is a ``Task``. You can ``wait()`` on
this task, or continue on to do other work.
The output to a ``tag`` operation is more :ref:`Tags` on that file. However, since the tag operations happens asynchronously on the back-end, you will
need to ``refresh()`` the file to see the output:

.. code-block:: python

   tagger_task = file.tag(tagger.handle)
   tagger_task.wait()

   # Refresh the file to see new tags
   file.refresh()

