Using Taggers
-------------

To use a tagger, create an instance within your workspace and then apply it to a file.
Note that a file must have first been :ref:`blockified<Blockifiers>` in order to be tagged.

.. code-block:: python

   # Load a Steamship Worksapce
   from steamship import Steamship, File
   client = Steamship(workspace="my-workspace-handle")

   # Upload a file
   importer = client.use_plugin("file-importer-handle", "instance-handle", config={})

   # Create a file via that plugin instance.
   file = File.create_with_plugin(client, plugin_instance=importer.handle)

   # Create the blockifier instance
   blockifier = client.use_plugin('blockifier-handle', 'instance-handle')

   # Apply the blockifier to the file
   blockifier_task = file.blockify(blockifier.handle)
   blockifier_task.wait()

   # Create the tagger instance
   tagger = client.use_plugin('tagger-handle', 'instance-handle')

   # Apply the tagger to the file
   tagger_task = file.tag(tagger.handle)
   tagger_task.wait()

   # Query across the persisted tags returned from tagging.
   file.query('blocktag AND name "paragraph"')


Using a Tagger from within a Steamship Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Steamship Packages are Python classes that run in the cloud. The Package
constructor receives a pre-configured Steamship client anchored in the
correct user Workspace for the lifespan of that instance. You should use
this client to import any File Importers that package uses.

Do that with the ``client.use_plugin`` method, like this:

.. code-block:: python

   from steamship import Steamship, App

   class MyPackage(App):
     def __init__(self, client: Steamship, config: Dict[str, Any] = None):
       super().__init__(client, config)
       self.tagger = client.use_plugin(
         plugin_handle="tagger-handle",
         instance_handle="unique-id",
         config={"key": "value"}
       )

       # Or, as a shortcut:
       self.tagger = client.use_plugin("tagger-handle", "unique-id", config={})

We recommend:

1) Doing this in the constructor, and saving the result as a member
   variable.
2) Using a pre-set instance handle. This will ensure you get the same
   plugin instance each time instead of generating a new one each time
   your package is used.

Using a Tagger from within a Steamship Workspace
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each instance of a Steamship client is anchored to a Workspace. This
Workspace provides a scope in which data and infrastructure can live.

Create a plugin instance within a Workspace by simply using the
Steamship client, like this:

.. code-block:: python

   from steamship import Steamship

   client = Steamship()

   tagger = client.use_plugin(
     plugin_handle="tagger-handle",
     instance_handle="unique-id",
     config={"key": "value"}
   )

   # Or, as a shortcut:

   tagger = client.use_plugin("tagger-handle", "unique-id", config={})

Using a Tagger as a one-off operation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you wish to use a Tagger in-line without a known workspace, you
can create a Tagger from the Steamship client’s static class.

.. code-block:: python

   from steamship import Steamship

   tagger = Steamship.use_plugin(
     plugin_handle="tagger-handle",
     config={"key": "value"}
   )

   # Or, as shorthand:

   tagger = Steamship.use_plugin("tagger-handle", config={})

This will create a new workspace in which your tagger instance will live.
