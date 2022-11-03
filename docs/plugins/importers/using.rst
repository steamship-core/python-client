Using File Importers
--------------------

To use a :ref:`file importer<File Importers>`, create an instance within your workspace and then refer to it when creating a file.

.. code-block:: python

   # Load a Steamship Worksapce
   from steamship import Steamship, File
   client = Steamship(workspace="my-workspace-handle")

   # Upload a file
   importer = client.use_plugin("file-importer-handle", "instance-handle", config={})

   # Create a file via that plugin instance.
   file = File.create_with_plugin(client, plugin_instance=importer.handle)

The documentation for the file importer you use will provide instructions about how to pass required arguments to it.
Some require configuration (provided at plugin instance creation time) and others require a URL (provided at file creation time).

Using a File Importer from within a Steamship Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
       self.importer = client.use_plugin(
         plugin_handle="file-importer-handle",
         instance_handle="unique-id",
         config={"key": "value"}
       )

       # Or, as a shortcut:
       self.importer = client.use_plugin("file-importer-handle", "unique-id", config={})

We recommend:

1) Doing this in the constructor, and saving the result as a member
   variable.
2) Using a pre-set instance handle. This will ensure you get the same
   plugin instance each time instead of generating a new one each time
   your package is used.

Using a File Importer from within a Steamship Workspace
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each instance of a Steamship client is anchored to a Workspace. This
Workspace provides a scope in which data and infrastructure can live.

Create a plugin instance within a Workspace by simply using the
Steamship client, like this:

.. code-block:: python

   from steamship import Steamship

   client = Steamship()

   importer = client.use_plugin(
     plugin_handle="file-importer-handle",
     instance_handle="unique-id",
     config={"key": "value"}
   )

   # Or, as a shortcut:

   importer = client.use_plugin("file-importer-handle", "unique-id", config={})

Using a File Importer as a one-off operation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you wish to use a File Importer in-line without a known workspace, you
can create a File Importer from the Steamship client’s static class.

.. code-block:: python

   from steamship import Steamship

   importer = Steamship.use_plugin(
     plugin_handle="file-importer-handle",
     config={"key": "value"}
   )

   # Or, as shorthand:

   importer = Steamship.use_plugin("file-importer-handle", config={})

This will create a new workspace in which your importer instance will live.
