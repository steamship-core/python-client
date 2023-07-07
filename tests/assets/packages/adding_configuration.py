"""
THIS SHOULD BE KEPT IN SYNC WITH THE DOCS: packages/adding-configuration.rst.
"""
from typing import Any, Dict, Type

from steamship import Steamship
from steamship.invocable import Config, InvocationContext, PackageService, post


class ConfigurableFavoritesPackage(PackageService):
    class FavoritesConfig(Config):
        """Configuration required to instantiate this package."""

        name: str
        favorite_color: str
        lucky_number: float
        favorite_true_false_value: bool

    def __init__(
        self, client: Steamship, config: Dict[str, Any] = None, context: InvocationContext = None
    ):
        # The superclass init method turns the config param (a Dict)
        # into the self.config object (here, a FavoritesConfig)
        super().__init__(client, config)

    # The config_cls method allows your package to return a class
    # that defines its required configuration.
    # See Developer Reference -> Accepting Configuration
    # for more details. This package uses a few configuration fields
    # to record the package user's favorite things.
    @classmethod
    def config_cls(cls) -> Type[Config]:
        return cls.FavoritesConfig

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
