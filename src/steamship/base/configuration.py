from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Optional

import inflection
from pydantic import BaseModel, HttpUrl

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


class CamelModel(BaseModel):
    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        super().__init__(**kwargs)

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


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

    def for_space(
        self, space_id: Optional[str] = None, space_handle: Optional[str] = None
    ) -> Configuration:
        """Return a new Configuration, identical to this, but anchored in a different space.

        Providing either `space_id` or `space_handle` will work; both need not be provided.
        """
        logging.info(f"Loading Configuration for_space: {self.api_key}")
        return Configuration(
            api_key=self.api_key,
            api_base=self.api_base,
            app_base=self.app_base,
            web_base=self.web_base,
            space_id=space_id,
            space_handle=space_handle,
        )
