.. _DevelopingPluginsSec:

Implementing Plugins
~~~~~~~~~~~~~~~~~~~~

From the implementation perspective, think of a plugin as a Python class that implements some abstract base class.
The specific abstract base class depends on the type of plugin you are writing.
If you've implemented the required abstract methods, you have successfully built a plugin.

Documentation and tips specific to plugin authoring is thus specific to the plugin as well.
You can find it here:

- :ref:`Developing File Importers<DevelopingFileImporters>`
- :ref:`Developing Blockifiers<DevelopingBlockifiersSec>`
- :ref:`Developing Taggers<DevelopingTaggers>`
- :ref:`Developing Embedders<DevelopingEmbedders>`

Unlike packages, plugins also offer support for asynchronous work.
This is useful when writing a plugin that, itself, contacts an asynchronous third-party API.
You can find the documentation for that here:

.. toctree::
   :maxdepth: 1

   Writing Async Plugins <async-plugins>
