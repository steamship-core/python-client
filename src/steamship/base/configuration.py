from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import inflection
from pydantic import HttpUrl

from steamship.base.error import SteamshipError
from steamship.base.model import CamelModel
from steamship.utils.utils import format_uri

DEFAULT_WEB_BASE = "https://app.steamship.com/"
DEFAULT_APP_BASE = "https://steamship.run/"
DEFAULT_API_BASE = "https://api.steamship.com/api/v1/"

ENVIRONMENT_VARIABLES_TO_PROPERTY = {
    "STEAMSHIP_API_KEY": "api_key",
    "STEAMSHIP_API_BASE": "api_base",
    "STEAMSHIP_APP_BASE": "app_base",
    "STEAMSHIP_WEB_BASE": "web_base",
    "STEAMSHIP_WORKSPACE_ID": "workspace_id",
    "STEAMSHIP_WORKSPACE_HANDLE": "workspace_handle",
}
DEFAULT_CONFIG_FILE = Path.home() / ".steamship.json"

# This stops us from including the `client` object in the dict() output, which is fine in a dict()
# but explodes if that dict() is turned into JSON. Sadly the `exclude` option in Pydantic doesn't
# cascade down nested objects, so we have to use this structure to catch all the possible combinations
EXCLUDE_FROM_DICT = {
    "client": True,
    "blocks": {"__all__": {"client": True, "tags": {"__all__": {"client": True}}}},
    "tags": {"__all__": {"client": True}},
}


class Configuration(CamelModel):
    api_key: str
    api_base: HttpUrl = DEFAULT_API_BASE
    app_base: HttpUrl = DEFAULT_APP_BASE
    web_base: HttpUrl = DEFAULT_WEB_BASE
    workspace_id: str = None
    workspace_handle: str = None
    profile: Optional[str] = None

    def __init__(
        self,
        config_file: Optional[Path] = None,
        **kwargs,
    ):
        # First set the profile
        kwargs["profile"] = profile = kwargs.get("profile") or os.getenv("STEAMSHIP_PROFILE")

        # Then load configuration from a file if provided
        config_dict = self._load_from_file(
            config_file or DEFAULT_CONFIG_FILE,
            profile,
            raise_on_exception=config_file is not None,
        )
        config_dict.update(self._get_config_dict_from_environment())
        kwargs.update({k: v for k, v in config_dict.items() if kwargs.get(k) is None})

        kwargs["api_base"] = format_uri(kwargs.get("api_base"))
        kwargs["app_base"] = format_uri(kwargs.get("app_base"))
        kwargs["web_base"] = format_uri(kwargs.get("web_base"))

        if not kwargs.get("api_key") and not kwargs.get("apiKey"):
            raise SteamshipError(
                "You're trying to access steamship without passing an api token. \n"
                "You can fix this error in two ways: \n"
                '\tOption 1: Directly pass your private api_key using `Steamship(api_key="YOUR-API-KEY")`. '
                "You can find your private api key on: https://app.steamship.com/key \n"
                "\tOption 2: Authenticate using the Steamship cli `npm install -g @steamship/cli && ship login`"
            )

        super().__init__(**kwargs)

    @staticmethod
    def _load_from_file(
        file: Path, profile: str = None, raise_on_exception: bool = False
    ) -> Optional[dict]:
        try:
            with file.open() as f:
                config_file = json.load(f)
                if profile:
                    if "profiles" not in config_file or profile not in config_file["profiles"]:
                        raise RuntimeError(f"Profile {profile} requested but not found in {file}")
                    config = config_file["profiles"][profile]
                else:
                    config = config_file
                return {inflection.underscore(k): v for k, v in config.items()}
        except FileNotFoundError:
            if raise_on_exception:
                raise Exception(f"Tried to load configuration file at {file} but it did not exist.")
        except Exception as err:
            if raise_on_exception:
                raise err
        return {}

    @staticmethod
    def _get_config_dict_from_environment():
        """Overrides configuration with environment variables."""
        return {
            property_name: os.getenv(environment_variable_name, None)
            for environment_variable_name, property_name in ENVIRONMENT_VARIABLES_TO_PROPERTY.items()
            if environment_variable_name in os.environ
        }
