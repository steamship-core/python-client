.. _Uploading Data:

Uploading Data
--------------

There are three ways to upload data to a workspace:

- :ref:`From a local file<Uploading a local file>`
- :ref:`From a URL<Uploading a URL>`
- :ref:`Via a Plugin<Uploading via Plugin>`

Each of these methods always results in a new  :ref:`File<Files>` object.

.. _Uploading a local file:

Uploading a local file
^^^^^^^^^^^^^^^^^^^^^^

Upload a file on disk with the ``File.create`` method.

If you pass a ``path`` argument to this method, the file will be read from disk:

.. code-block:: python

   file = File.create(
      client=client,
      path="path/to/some_file"
   ).data

If you pass a ``content`` argument to this method, the file will be created from the provided string:

.. code-block:: python

   file = File.create(
      client=client,
      content="String content"
   ).data

If you pass a ``blocks`` argument to this method, you can provided structured, pre-created :ref:`Blocks`,
removing the need to :ref:`blockify<Blockifiers>` your file later.

.. code-block:: python

   file = File.create(
      client=client,
      blocks=Block.CreateRequest(...)
   ).data

.. _Uploading via Plugin:

Uploading via Plugin
^^^^^^^^^^^^^^^^^^^^

:ref:`Importer plugins<File Importers>` provide a way to perform more complex imports to Steamship.

For example, a Notion File Importer might implement the logic necessary to authenticate against Notion and fetch the data corresponding to a particular page.
This might be paired with a Notion File Blockifier that converts Notion's API response format into :ref:`Steamship Block Format<Data Model>`

To upload a file via a Plugin, first create an instance of the plugin in your workspace and then provide that instance to the ``File.create_with_plugin`` command.
Unlike uploading a file directly, uploading a file via an :ref:`Importer plugins<File Importers>` returns a ``Task`` object.

.. code-block:: python

   importer = client.use_plugin("plugin-handle", "instance-handle", config={})
   task = File.create_with_plugin(
      client=client,
      plugin_instancenstance=importer.handle
   )
   task.wait()
   file = File.parse_obj(task.output)
