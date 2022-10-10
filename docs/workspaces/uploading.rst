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

.. code:: python

   file = File.create(
      client=client,
      path="path/to/some_file"
   ).data

If you pass a ``content`` argument to this method, the file will be created from the provided string:

.. code:: python

   file = File.create(
      client=client,
      content="String content"
   ).data

If you pass a ``blocks`` argument to this method, you can provided structured, pre-created :ref:`Blocks`,
removing the need to :ref:`blockify<Blockifiers>` your file later.

.. code:: python

   file = File.create(
      client=client,
      blocks=Block.CreateRequest(...)
   ).data

.. _Uploading a URL:

Uploading a URL
^^^^^^^^^^^^^^^

Upload the file resolved by some URL by providing it to the ``File.create`` method.

.. code:: python

   file = File.create(
      client=client,
      url=url
   ).data

.. _Uploading via Plugin:

Uploading via Plugin
^^^^^^^^^^^^^^^^^^^^

:ref:`File Importer plugins<File Importers>` provide a way to perform more complex imports to Steamship.

For example, a Notion File Importer might implement the logic necessary to authenticate against Notion and fetch the data corresponding to a particular page.
This might be paired with a Notion File Blockifier that converts Notion's API response format into :ref:`Steamship Block Format<Data Model>`

To upload a file via a Plugin, first create an instance of the plugin in your workspace and then provide that instance to the ``File.create`` command:

.. code:: python

   importer = client.use_plugin("plugin-handle", "instance-handle", config={})
   importer = File.create(
      client=client,
      pluginInstance=importer.handle
   )
