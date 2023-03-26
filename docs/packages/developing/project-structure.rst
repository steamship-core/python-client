Package Project Structure
~~~~~~~~~~~~~~~~~~~~~~~~~

Your main implementation lives in the  ``src/api.py`` file of your project.
This file will have been created for you by the template you selected when starting your project.

- If you are developing a package, you will find a class that derives from the ``Invocable`` base class
- If you are developing a plugin, you will find a class that derives from a base class specific to the plugin type.

In both cases, this ``src/api.py`` template concludes by setting a ``handler`` variable that is required by the Steamship bootloader for cloud operation.

From the implementation perspective, think of a package as a Flask app.
It looks and feels like a regular Python class,
but its methods are decorated with decorators bind them to HTTP endpoints.
You can call instances of your package over HTTP, or you can use a Steamship client library wrapper.

Consider the following package:

.. code-block:: python

   class MyPackage(App):
       @get("say_hello")
       def _method_name_need_not_match(self, name: str = None) -> Response:
           return Response(string=f"Hello, {name}")

       @post("do_something")
       def do_something(self, number: int = None) -> Response:
           return Response(json={"number": number})

Once deployed to Steamship, every new instance of this package would be associated with two HTTP endpoints:

- Expose an HTTP GET endpoint at ``/say_hello`` that accepts a URL Querystring argument named ``name`` and returns a string response
- Expose an HTTP POST endpoint at ``/do_something`` that accepts a random number and returns it in a JSON object

These per-instance endpoints could also be called using convenience functions in the Steamship Python client:

.. code-block:: python

   # Create or reuse an instance of the package
   instance = Steamship.use("my-package", "instance-id")

   # Invoke the methods
   hello_resp = instance.invoke("say_hello", verb="GET", name="Ted")
   do_resp = instance.invoke("do_something", number=5)

A few rules about writing package methods:

- The ``@get`` and ``@post`` decorators declare HTTP ``GET`` and ``POST`` endpoints, respectively
- All method arguments **must be** kwargs with defaults
- The method's kwargs will be supplied by merging URL query parameters, form-encoded POST data, and JSON-encoded POST data.
- Binary input isn't yet supported. (Email us at hello@steamship.com for workarounds if you need one).
- All methods must return a ``Response`` object

For more examples of writing package endpoints, see the `example app <https://github.com/steamship-core/python-client/blob/main/tests/assets/apps/demo_app.py>`_ from our unit testing suite.

.. _Package Accepting Configuration

Accepting Configuration
-----------------------

Packages can take configuration parameters. Defining the configuration
for your Package requires users to provide values for these parameters when they
create an instance of your Package.

To define the configuration for your Package, create a class that inherits from Config:

.. code-block:: python

   class MyPackageConfig(Config):
        my_string_config_param: str = Field("my-default-value",
                                    description="A param this package needs which is a string.")
        my_numeric_config_param: float = Field(description="A numeric param this package needs.")

and then return this class from your Package's ``config_cls`` class method:

.. code-block:: python

   class MyPackageClass(Tagger):
       config: MyPackageConfig

       @classmethod
       def config_cls(cls) -> Type[Config]:
            return MyPackageConfig

This will guarantee that ``my_string_config_param`` and ``my_numeric_config_param`` are set for all invocations
of your package.  Since ``my_strong_config_param`` provides a default value, the user can omit it
from their configuration and the value ``"my-default-value"`` will be used.  Since ``my_numeric_config_param``
does not have a default value, a user *must* supply a value to create an instance of your package.

.. note::
    There is currently no such thing as an optional configuration parameter. All parameters that do
    not have a default value must have a value provided by the user at Package instantiation.

To use the config values within your package code, you can then refer to them from ``self.config``,
as in ``self.config.my_numeric_config_param``.  They will be automatically populated with the user's
data by Steamship when invoking your Package.