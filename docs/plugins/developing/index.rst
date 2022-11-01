.. _DevelopingPluginsSec:

Developing Plugins
~~~~~~~~~~~~~~~~~~

From the implementation perspective, think of a plugin as a Python class that implements some abstract base class.
The specific abstract base class depends on the type of plugin you are writing.
If you've implemented the required abstract methods, you have successfully built a plugin.

Read more here:

.. toctree::
   :maxdepth: 1

   Plugin Project Structure <project-structure>
   Developing Importers <importers>
   Developing Blockifiers <blockifiers>
   Developing Taggers <taggers>
   Developing Embedders <embedders>

Unlike packages, plugins also offer support for asynchronous work.
This is useful when writing a plugin that, itself, contacts an asynchronous third-party API.
You can find the documentation for that here:

.. toctree::
   :maxdepth: 1

   Writing Async Plugins <async-plugins>
