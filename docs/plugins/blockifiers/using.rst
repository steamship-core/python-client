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

   # Query across the persisted blocks and tags returned from blockification.
   file.query('blocktag AND name "paragraph"')

In the above code, the two key lines are:

.. code-block:: python

   blockifier = client.use_plugin('blockifier-handle', 'instance-handle')
   task = file.blockify(blockifier.handle)

In these lines, ``blockifier-handle`` identifies which blockifier you would like to use, and
``instance-handle`` identifies your particular instance of this blockifier in a workspace.
The same instance is reused, rather than created, if you load it like this again.

Common Blockifiers
~~~~~~~~~~~~~~~~~~

Steamship maintains a growing collection of official blockifiers for common scenarios.
Our goal is to always map our defaults to best of breed models so that you can get work done quickly without worrying
about the details of model selection and tuning.

Our current list of supported blockifiers are:

* `markdown-default <https://www.steamship.com/plugins/markdown-blockifier-default>`_ - Converts Markdown to Steamship Blocks
* `speech-to-text-default <https://www.steamship.com/plugins/s2t-blockifier-default>`_ - Converts audio to Steamship Blocks
* `whisper-s2t-blockifier <https://www.steamship.com/plugins/whisper-s2t-blockifier>`_ - Converts audio to Steamship Blocks (via `Whisper <https://openai.com/blog/whisper/>`_) 
* `wikipedia-blockifier <https://www.steamship.com/plugins/wikipedia-blockifier>`_ - Converts Wikipedia pages to Steamship Blocks
* `csv-blockifier <https://www.steamship.com/plugins/csv-blockifier>`_ - Converts CSV to Steamship Blocks

Using a Blockifier from within a Steamship Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Steamship Packages are Python classes that run in the cloud. The Package
constructor receives a pre-configured Steamship client anchored in the
correct user Workspace for the lifespan of that instance. You should use
this client to import any Blockifiers that package uses.

Do that with the ``client.use_plugin`` method, like this:

.. code-block:: python

   from steamship import Steamship, App

   class MyPackage(App):
     def __init__(self, client: Steamship, config: Dict[str, Any] = None):
       super().__init__(client, config)
       self.blockifier = client.use_plugin(
         plugin_handle="blockifier-handle",
         instance_handle="unique-id",
         config={"key": "value"}
       )

       # Or, as a shortcut:
       self.blockifier = client.use_plugin("blockifier-handle", "unique-id", config={})

We recommend:

1) Doing this in the constructor, and saving the result as a member
   variable.
2) Using a pre-set instance handle. This will ensure you get the same
   plugin instance each time instead of generating a new one each time
   your package is used.

Using a Blockifier from within a Steamship Workspace
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each instance of a Steamship client is anchored to a Workspace. This
Workspace provides a scope in which data and infrastructure can live.

Create a plugin instance within a Workspace by simply using the
Steamship client, like this:

.. code-block:: python

   from steamship import Steamship

   client = Steamship()

   blockifier = client.use_plugin(
     plugin_handle="blockifier-handle",
     instance_handle="unique-id",
     config={"key": "value"}
   )

   # Or, as a shortcut:

   blockifier = client.use_plugin("blockifier-handle", "unique-id", config={})

Using a Blockifier as a one-off operation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you wish to use a Blockifier in-line without a known workspace, you
can create a Blockifier from the Steamship client’s static class.

.. code-block:: python

   from steamship import Steamship

   blockifier = Steamship.use_plugin(
     plugin_handle="blockifier-handle",
     config={"key": "value"}
   )

   # Or, as shorthand:

   blockifier = Steamship.use_plugin("blockifier-handle", config={})
