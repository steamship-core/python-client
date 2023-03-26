.. _Using Plugins:

Using Plugins
=======

`Steamship Plugins <https://www.steamship.com/plugins>`_ perform specific tasks related to AI.

This page is about using existing plugins. If you want to develop a ``Plugin``, see :ref:`DevelopingPluginsSec`

Steamship supports the following types of plugins:


- :ref:`File Importers` pull raw data from common external sources into :ref:`Files`.
- :ref:`Blockifiers` extract text and other content from raw data from :ref:`Files` to :ref:`Blocks`.
- :ref:`Taggers` create :ref:`Tags` (annotations) on :ref:`Files` and :ref:`Blocks`.
- :ref:`Generators` create new :ref:`Blocks` (content) from existing :ref:`Blocks` (content).
- :ref:`Embedders` convert content into a vector representation. This is primarily used in combination with Steamship's built in Embedding Search.


.. _Creating Plugin Instances:

Plugin Instances
----------------

To use a ``Plugin``, create an instance of it. When building into a :ref:`Package<Packages>`, We recommend doing this in the constructor, and saving the result as a member
variable.

.. code-block:: python

    gpt4 = steamship.use_plugin("gpt-4")

``gpt4`` is now a ``PluginInstance``. The instance contains the plugin's configuration and is locked to the current version of the ``Plugin``.

To use a specific version of the ``Plugin``, pass the version handle:

.. code-block:: python

    gpt4 = steamship.use_plugin("gpt-4", version="0.0.1-rc.4")

To override default configuration parameters or provide required configuration values, pass a ``dict`` of values in the ``config`` parameter:

.. code-block:: python

    gpt4 = steamship.use_plugin("gpt-4", config={"max_tokens":1024})

To see available configuration parameters, check the documentation of the specific ``Plugin``.

To use a ``PluginInstance``, call the type-specific methods on it:

.. code-block:: python

    result_task = gpt4.generate(text="What's up GPT?")

Plugin invocations return asynchronous :ref:`Tasks` so that you can easily run many plugins and control when you need
the results.


See the plugin individual plugin types for further info on how each can be called.

.. toctree::
   :hidden:

   File Importers <importers/index>
   Blockifiers <blockifiers/index>
   Taggers <taggers/index>
   Generators <generators/index>
   Embedders <embedders/index>
   Tasks <tasks>
