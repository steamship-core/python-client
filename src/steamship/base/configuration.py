from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import inflection
from pydantic import BaseModel, HttpUrl
from pydantic.generics import GenericModel

from steamship.base.utils import format_uri, to_camel

DEFAULT_WEB_BASE = "https://app.steamship.com/"
DEFAULT_APP_BASE = "https://steamship.run/"
DEFAULT_API_BASE = "https://api.steamship.com/api/v1/"

ENVIRONMENT_VARIABLES_TO_PROPERTY = {
    "STEAMSHIP_API_KEY": "api_key",
    "STEAMSHIP_API_BASE": "api_base",
    "STEAMSHIP_APP_BASE": "app_base",
    "STEAMSHIP_WEB_BASE": "web_base",
    "STEAMSHIP_SPACE_ID": "space_id",
    "STEAMSHIP_SPACE_HANDLE": "space_handle",
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


class CamelModel(BaseModel):
    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        super().__init__(**kwargs)

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        # Populate enum values with their value, rather than the raw enum. Important to serialise model.dict()
        use_enum_values = True

    def dict(self, **kwargs) -> dict:
        exclude_set = {}
        exclude_set.update(EXCLUDE_FROM_DICT)

        if "exclude" in kwargs:
            if isinstance(kwargs["exclude"], set):
                for key in kwargs["exclude"]:
                    exclude_set[key] = True
            elif isinstance(kwargs["exclude"], dict):
                exclude_set.update(kwargs["exclude"])

        kwargs["exclude"] = exclude_set
        return super().dict(**kwargs)


class GenericCamelModel(CamelModel, GenericModel):
    pass


class Configuration(CamelModel):
    api_key: str
    api_base: Optional[HttpUrl] = DEFAULT_API_BASE
    app_base: Optional[HttpUrl] = DEFAULT_APP_BASE
    web_base: Optional[HttpUrl] = DEFAULT_WEB_BASE
    space_id: str = None
    space_handle: str = None
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
