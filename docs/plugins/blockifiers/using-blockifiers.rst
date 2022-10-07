Importing and Using Blockifiers
===============================

Importing a Blockifier
----------------------

From within a Steamship Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Steamship Packages are Python classes that run in the cloud. The Package
constructor receives a pre-configured Steamship client anchored in the
correct user Workspace for the lifespan of that instance. You should use
this client to import any Blockifiers that package uses.

Do that with the ``client.use_plugin`` method, like this:

.. code:: python

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

From within a Steamship Workspace
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each instance of a Steamship client is anchored to a Workspace. This
Workspace provides a scope in which data and infrastructure can live.

Create a plugin instance within a Workspace by simply using the
Steamship client, like this:

.. code:: python

   from steamship import Steamship

   client = Steamship()

   blockifier = client.use_plugin(
     plugin_handle="blockifier-handle",
     instance_handle="unique-id",
     config={"key": "value"}
   )

   # Or, as a shortcut:

   blockifier = client.use_plugin("blockifier-handle", "unique-id", config={})

Inside its own Workspace
~~~~~~~~~~~~~~~~~~~~~~~~

If you wish to use a Blockifier in-line without a known workspace, you
can create a Blockifier from the Steamship client’s static class.

.. code:: python

   from steamship import Steamship

   blockifier = Steamship.use_plugin(
     plugin_handle="blockifier-handle",
     config={"key": "value"}
   )

   # Or, as shorthand:

   blockifier = Steamship.use_plugin("blockifier-handle", config={})

Using a blockifier
------------------

Once imported, you can use your blockifier in two ways:

-  **Statefully, on workspace data.** This will render some file in
   Steamship available for processing and querying by other plugins.
-  **Statelessly, on inline data.** This will return the blockifier’s
   output in Steamship Block format without saving it to your Workspace.

Using a Blockifier statefully on Workspace data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use a blockfier statefully on a file in a workspace, call the
``file.blockify``, passing in the blockifier. The results are saved in
your workspace so that you never need to perform that operation again.

.. code:: python

   # TODO: Check the below code for correctness

   # Load a Steamship Worksapce 
   from steamship import Steamship, File
   client = Steamship(workspace="my-workspace-handle")

   # Upload a Markdown file
   file = File.create(path="path/to/markdown_file.md").data

   # Blockify the file.
   blockifier = client.use_plugin("markdown-blockifier")
   task = file.blockify(plugin_instance=blockifier.handle)

   # Wait until the blockify task completes remotely
   task.wait()

   # Query across the persisted blocks and tags returned from blockification.
   file.query("""
       blocktag AND name "paragraph" AND contains "foobar"
   """)

Using a Blockifier statelessly on inline data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TODO