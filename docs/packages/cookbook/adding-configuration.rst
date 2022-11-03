Making a package or plugin user-configurable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This example demonstrates how to make your package or plugin configurable by a user. To add configuration to your package or plugin, you need to do a few things.

First, you need to declare a ``configTemplate`` in your ``steamship.json``.

.. code-block:: json

    {
        "type": "package",
        "handle": "a-configurable-package",
        ...
        "configTemplate": {
            "name": {
                "type": "string",
                "description": "The name of the user.",
                "default": "you"
            },
            "favorite_color": {
                "type": "string",
                "description": "The user's favorite color."
            },
            "lucky_number": {
                "type": "number",
                "description": "The user's lucky number"
            },
            "favorite_true_false_value": {
                "type": "string",
                "description": "The user's favorite boolean value, true or false."
            }
        }
    }

With this ``configTemplate`` in the ``steamship.json``, Steamship users will be required to
provide a configuration when instantiating this package:

.. code-block:: python

    Steamship.use("a-configurable-package", config={
        "name": "Dave",
        "favorite_color": "blue",
        "lucky_number": 6,
        "favorite_true_false_value": False
    })

This config will be validated at the time of instance creation for completeness and correct types.

Since we provided a default value for ``name`` in the template, that value can be omitted and ``"you"``
will be used instead.

Now, within the code, you must do a few things.  First, you define the inner class that represents the configuration:

.. code-block:: python

    class ConfigurableFavoritesPackage(PackageService):
        class FavoritesConfig(Config):
            """Configuration required to instantiate this package."""

            name: str
            favorite_color: str
            lucky_number: float
            favorite_true_false_value: bool

The names of the fields **must** align with the names in the ``configTemplate``.

Next, we tell the Steamship handler how to find our config class:

.. code-block:: python

    class ConfigurableFavoritesPackage(PackageService):
        ...
        def config_cls(self) -> Type[Config]:
            return self.FavoritesConfig

Now when implementing a method, we can use the config fields via ``self.config.<field_name>``!

.. code-block:: python

    @post("my_faves")
    def my_faves(self) -> str:
        """Return the user's favorites, in a string."""

        return f"""
        Hey {self.config.name}!
        I can remind you of your favorites.
        Your favorite color is {self.config.favorite_color}.
        Your lucky number is {self.config.lucky_number}.
        Your favorite true/false value is {self.config.favorite_true_false_value}.
        Wow, mine too!
        """

When you put it all together, it looks like this:

.. code-block:: python

    """
    This package demonstrates how configuration works in Steamship.
    """
    from typing import Dict, Any, Type

    from steamship import Steamship
    from steamship.invocable import PackageService, Config, post, create_handler


    class ConfigurableFavoritesPackage(PackageService):
        class FavoritesConfig(Config):
            """Configuration required to instantiate this package."""

            name: str
            favorite_color: str
            lucky_number: float
            favorite_true_false_value: bool

        def __init__(self, client: Steamship, config: Dict[str, Any] = None):
            # The superclass init method turns the config param (a Dict)
            # into the self.config object (here, a FavoritesConfig)
            super().__init__(client, config)


        # The config_cls method allows your package to return a class
        # that defines its required configuration.
        # See Developer Reference -> Accepting Configuration
        # for more details. This package uses a few configuration fields
        # to record the package user's favorite things.
        def config_cls(self) -> Type[Config]:
            """Return our config object"""
            return self.FavoritesConfig

        # This method defines the package user's endpoint for adding content
        # The @post annotation automatically makes the method available as
        # an HTTP Post request. The name in the annotation defines the HTTP
        # route suffix, see Packages -> Package Project Structure.
        @post("my_faves")
        def my_faves(self) -> str:
            """Return the user's favorites, in a string."""

            return f"""
            Hey {self.config.name}!
            I can remind you of your favorites.
            Your favorite color is {self.config.favorite_color}.
            Your lucky number is {self.config.lucky_number}.
            Your favorite true/false value is {self.config.favorite_true_false_value}.
            Wow, mine too!
            """


    # This line connects our Package implementation class to the surrounding
    # Steamship handler code.
    handler = create_handler(ConfigurableFavoritesPackage)
