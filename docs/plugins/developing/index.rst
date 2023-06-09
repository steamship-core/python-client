.. _DevelopingPluginsSec:

Developing Plugins
~~~~~~~~~~~~~~~~~~

Each plugin is a stateless, Python-based microservice that runs in the
cloud and conforms to a strict interface and data model. Plugins may do
work themselves, or they may adapt work done by third-party services for
use with Steamship.

To implement a plugin, you simply fill in the required abstract methods from the appropriate ``PluginService`` abstract class.
If you've implemented the required abstract methods, you have successfully built a plugin!

Read more here:

.. toctree::
   :maxdepth: 1

   Plugin Project Structure <project-structure>
   Developing File Importers <importers>
   Developing Blockifiers <blockifiers>
   Developing Generators <generators>
   Developing Taggers <taggers>
   Developing Embedders <embedders>

Unlike packages, plugins also offer support for asynchronous work.
This is useful when writing a plugin that, itself, contacts an asynchronous third-party API.
You can find the documentation for that here:

.. toctree::
   :maxdepth: 1

   Writing Async Plugins <async-plugins>

