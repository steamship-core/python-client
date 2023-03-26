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

.. _Plugin Accepting Configuration

Accepting Configuration
-----------------------

Plugins, like packages, can take configuration parameters. Defining the configuration
for your Plugin requires users to provide values for these parameters when they
create an instance of your Plugin.

To define the configuration for your Plugin, create a class that inherits from Config:

.. code-block:: python

   class MyPluginConfig(Config):
        my_string_config_param: str = Field("my-default-value",
                                    description="A param this plugin needs which is a string.")
        my_numeric_config_param: float = Field(description="A numeric param this plugin needs.")

and then return this class from your Plugin's ``config_cls`` class method:

.. code-block:: python

   class MyPluginClass(Tagger):
       config: MyPluginConfig

       @classmethod
       def config_cls(cls) -> Type[Config]:
            return MyPluginConfig

This will guarantee that ``my_string_config_param`` and ``my_numeric_config_param`` are set for all invocations
of your plugin.  Since ``my_strong_config_param`` provides a default value, the user can omit it
from their configuration and the value ``"my-default-value"`` will be used.  Since ``my_numeric_config_param``
does not have a default value, a user *must* supply a value to create an instance of your plugin.

To use the config values within your plugin code, you can then refer to them from ``self.config``,
as in ``self.config.my_numeric_config_param``.  They will be automatically populated with the user's
data by Steamship when invoking your Plugin.

