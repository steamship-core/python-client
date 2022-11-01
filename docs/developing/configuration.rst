Accepting Configuration
-----------------------

Your plugin may need to accept configuration to be usable.
Examples might include:

- An API key that your plugin needs to invoke a third-party service
- A parameter setting, such as a threshold or output class

Your plugin's :ref:`Steamship Manifest<Steamship Manifest Files>` file contains a property
called ``configTemplate`` which enables you to define and strongly type this configuration.

.. _configTemplate Schema:

Declaring your plugin's configuration template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``configTemplate`` property in your plugin's ``steamship.json`` file defines a schema
for your plugin's configuration.
This configuration is provided upon each new instance creation, and it is
frozen and saved with your instance for reuse.

The value of the ``configTemplate`` block takes the following form:

.. code-block:: json

   {
     "configTemplate": {
       "param_name": {
         "type": "boolean",
         "description": "Whether something should be enabled..",
         "default": false
       },
       "param_name_2": {
         "type": "string",
         "description": "Some string parameter.",
       }

     }
   }

In the above code, you can see that the parameter name is the key of the
object, and details about that parameter are in the associated body.
Those details are:

-  ``type`` - Either ``boolean``, ``string``, or ``number``.
-  ``description`` - A short description of the parameter.
-  ``default`` A default value if the user does not provide one.

If a parameter does not have a default value, and a Steamship user tries
to create a new instance without specifying it, that instance creation
will fail.

Defining and using configuration in your plugin code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After defining your ``configTemplate``, you must create a matching object in your plugin's Python implementation.
This object should extend the ``steamship.plugin.config.Config`` class.

.. code-block:: python

   from steamship.plugin.config import Config

   class MyPluginConfig(Config):
       """Config object containing required parameters to initialize
       a MyPlugin object."""

       param_name: bool = False
       param_name_2: str

In your plugin class, you will also have to return this object from the abstract ``config_cls`` method.
This enables the plugin loader to construct the correct configuration object for your plugin.

.. code-block:: python

   class MyPlugin(Blockifier):
      def config_cls(self) -> Type[Config]:=
         return MyPluginConfig

Finally, your plugin's base class will always make available a ``self.config`` object whose type
matches the type returned by ``MyPlugin``.

When users create new instances of your plugin, the configuration will be type checked against the
schema provided in ``steamship.json``, and loaded at runtime into the object returned by ``config_cls``
