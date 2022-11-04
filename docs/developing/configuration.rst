Accepting Configuration
-----------------------

Your package or plugin may need to accept configuration to be usable.
Examples might include:

- An API key to invoke a third-party service
- A parameter setting, such as a threshold or output class

Your package or plugin's :ref:`Steamship Manifest<Steamship Manifest Files>` file contains a property
called ``configTemplate`` which enables you to define and strongly type this configuration.

.. _configTemplate Schema:

Declaring your configuration template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``configTemplate`` property in your ``steamship.json`` file defines a schema
for your package or plugin's configuration.
This configuration is provided upon each new instance creation, and it is
frozen and saved with the instance for reuse.

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
-  ``default`` - A default value if the user does not provide one.

If a parameter does not have a default value, and a Steamship user tries
to create a new instance without specifying it, that instance creation
will fail. Similarly, provided values with incorrect types will be rejected. This
means that your package or plugin is guaranteed to receive a config that structurally
matches your ``configTemplate``.

Defining and using configuration in your code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After defining your ``configTemplate``, you must create a matching object in your package or plugin's Python implementation.
This object should extend the ``steamship.invocable.Config`` class.

.. code-block:: python

   from steamship.invocable import Config

   class MyPluginConfig(Config):
       """Config object containing required parameters to initialize
       a MyPlugin object."""

       param_name: bool = False
       param_name_2: str

In your class, you will also have to return this object from the abstract ``config_cls`` method.
This enables the package or plugin loader to construct the correct configuration object.

.. code-block:: python

   class MyPlugin(Blockifier):
      def config_cls(self) -> Type[Config]:=
         return MyPluginConfig

Finally, your package or plugin's base class will always make available a ``self.config`` object whose type
matches the type returned by ``config_cls``.

When users create new instances of your package plugin, the configuration will be type checked against the
schema provided in ``steamship.json``. When the instance is invoked, the configuration will be
loaded at runtime into ``self.config``.
