Accepting Configuration
-----------------------

Your package or plugin may need to accept configuration to be usable.
Examples might include:

- An API key to invoke a third-party service
- A parameter setting, such as a threshold or output class

A configuration parameter has:
-  ``type`` - Either ``boolean``, ``string``, or ``number``.
-  ``description`` - A short description of the parameter.
-  ``default`` - A default value if the user does not provide one.

If a parameter does not have a default value, and a Steamship user tries
to create a new instance without specifying it, that instance creation
will fail. Similarly, provided values with incorrect types will be rejected. This
means that your package or plugin is guaranteed to receive a config that structurally matches.

.. note::
    There is currently no such thing as an optional configuration parameter. All parameters that do
    not have a default value must have a value provided by the user at Package instantiation.


.. _Accepting Configuration:

Defining and Accepting configuration in your code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


To define the configuration for your Package, create a class that inherits from Config:

.. code-block:: python

   class MyPackageConfig(Config):
        my_string_config_param: str = Field("my-default-value",
                                    description="A param this package needs which is a string.")
        my_numeric_config_param: float = Field(description="A numeric param this package needs.")

and then return this class from your package or plugin's ``config_cls`` class method:

.. code-block:: python

   class MyPackageClass(PackageService):
       config: MyPackageConfig

       @classmethod
       def config_cls(cls) -> Type[Config]:
            return MyPackageConfig

This will guarantee that ``my_string_config_param`` and ``my_numeric_config_param`` are set for all invocations
of your package or plugin.  Since ``my_strong_config_param`` provides a default value, the user can omit it
from their configuration and the value ``"my-default-value"`` will be used.  Since ``my_numeric_config_param``
does not have a default value, a user *must* supply a value to create an instance of your package or plugin.

To use the config values within your code, you can then refer to them from ``self.config``,
as in ``self.config.my_numeric_config_param``.  They will be automatically populated with the user's
data by Steamship when invoking your package or plugin.



