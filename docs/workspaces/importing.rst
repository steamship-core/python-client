.. _Importing Data:

Importing Data
--------------

Importing content to your Workspace is the first step to processing it.
Here are some ways to do it:

- :ref:`Import content directly<Import content directly>`
- :ref:`Import content via a Plugin<Import content via a Plugin>`

Each of these methods always results in a new  :ref:`File<Files>` object.
**But you can't use it yet!**
After you import a File, you must :ref:`Blockify<Blockifying Data>` to transform it into Steamship format.

.. _Import content directly:

Import content directly
^^^^^^^^^^^^^^^^^^^^^^^

Import a file on disk with the ``File.create`` method.

If you pass a ``content`` argument to this method, a file will be created from the provided string.
An optional ``mime_type`` argument can also be provided.

.. tab:: Python

    .. code-block:: python

       import { Steamship, MimeTypes } from "@steamship/client"
       client = Steamship()

       file = File.create(
          client=client,
          content="String content",
          mime_type=MimeTypes.MKD
       )


For local files, ``content`` can be supplied via` ``read()``. If the file is a binary file, you may want to supply
a custom MIME type, via the ``mime_type`` parameter.

If you pass a ``blocks`` argument to this method, you can provided structured, pre-created :ref:`Blocks`,
removing the need to :ref:`blockify<Blockifiers>` your file later.

.. tab:: Python

    .. code-block:: python

       import { Steamship, MimeTypes } from "@steamship/client"
       client = Steamship()

       file = File.create(
          client=client,
          blocks=Block.CreateRequest(...)
       )

.. _Import content via a Plugin:

Import content via a Plugin
^^^^^^^^^^^^^^^^^^^^^^^^^^^

:ref:`Importer Plugins<File Importers>` provide a way to perform more complex imports to Steamship.

For example, a Notion File Importer might implement the logic necessary to authenticate against Notion and fetch the data corresponding to a particular page.
This might be paired with a Notion File Blockifier that converts Notion's API response format into :ref:`Steamship Block Format<Data Model>`

To import a file via a Plugin, first create an instance of the plugin in your workspace and then provide that instance to the ``File.create_with_plugin`` command.
Unlike importing a file directly, importing a file via an :ref:`Importer plugins<File Importers>` returns a ``Task`` object.

.. tab:: Python

    .. code-block:: python

       import { Steamship } from "@steamship/client"
       client = Steamship()

       importer = client.use_plugin("importer-plugin-handle")
       task = File.create_with_plugin(
          client=client,
          plugin_instance=importer.handle
       )
       task.wait()

       # Refresh the file from remote
       file = file.refresh()
