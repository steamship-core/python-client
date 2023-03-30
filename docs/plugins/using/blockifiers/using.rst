Using Blockifiers
-----------------

To use a blockifier, create an instance with your Steamship client and apply it to a file.

.. code-block:: python

   # Load a Steamship Workspace
   from steamship import Steamship, File
   client = Steamship(workspace="my-workspace-handle")

   # Upload a file
   file = File.create(path="path/to/some_file").data

   # Create the blockifier instance
   blockifier = client.use_plugin('blockifier-handle', 'instance-handle')

   # Apply the blockifier to the file
   task = file.blockify(blockifier.handle)

   # Wait until the blockify task completes remotely
   task.wait()

   # Refresh the file to see the output
   file.refresh()

   # file.blocks now has the blockified content

In the above code, the two key lines are:

.. code-block:: python

   blockifier = client.use_plugin('blockifier-handle')
   task = file.blockify(blockifier.handle)

In these lines, ``blockifier-handle`` identifies which blockifier you would like to use, and
``instance-handle`` identifies your particular instance of this blockifier in a workspace.
The same instance is reused, rather than created, if you load it like this again.

Common Blockifiers
~~~~~~~~~~~~~~~~~~

Steamship maintains a growing collection of official blockifiers for common scenarios.
Our goal is to always map our defaults to best of breed models so that you can get work done quickly without worrying
about the details of model selection and tuning.

Our currently supported blockifiers are:

* `markdown-default <https://www.steamship.com/plugins/markdown-blockifier-default>`_ - Converts Markdown to Steamship Blocks
* `speech-to-text-default <https://www.steamship.com/plugins/s2t-blockifier-default>`_ - Converts audio to Steamship Blocks
* `whisper-s2t-blockifier <https://www.steamship.com/plugins/whisper-s2t-blockifier>`_ - Converts audio to Steamship Blocks (via `Whisper <https://openai.com/blog/whisper/>`_) 
* `wikipedia-blockifier <https://www.steamship.com/plugins/wikipedia-blockifier>`_ - Converts Wikipedia pages to Steamship Blocks
* `csv-blockifier <https://www.steamship.com/plugins/csv-blockifier>`_ - Converts CSV to Steamship Blocks


Input
-----

The input to a ``blockify`` operation is a ``File`` with no ``Blocks``.

Output
------

When you call ``blockify`` on a file, the object that is returned is a ``Task``. You can ``wait()`` on
this task, or continue on to do other work.
The output of a ``blockify`` operation is :ref:`Blocks` and potentially :ref:`Tags` on that file. However, since the operation happens asynchronously on the back-end, you will
need to ``refresh()`` the file to see the output.