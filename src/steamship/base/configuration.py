from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Optional

import inflection
from pydantic import BaseModel

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
    api_key: str = None
    api_base: str = None
    app_base: str = None
    web_base: str = None
    space_id: str = None
    space_handle: str = None
    profile: Optional[str] = None

    def __init__(
        self,
        config_file: Optional[Path] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        # First set the profile
        self.profile = self.profile or os.getenv("STEAMSHIP_PROFILE")

        # Then load configuration from a file if provided
        config_dict = self._load_from_file(
            config_file or DEFAULT_CONFIG_FILE,
            self.profile,
            raise_on_exception=config_file is not None,
        )
        config_dict.update(self._get_config_dict_from_environment())
        self._update(config_dict)

        self.api_base = self.api_base or DEFAULT_API_BASE
        self.api_base = format_uri(self.api_base)

        self.app_base = self.app_base or DEFAULT_APP_BASE
        self.app_base = format_uri(self.app_base)

        self.web_base = self.web_base or DEFAULT_WEB_BASE
        self.web_base = format_uri(self.web_base)

    def _update(self, config_dict: dict, override: bool = False) -> None:
        config_dict = {inflection.underscore(k): v for k, v in config_dict.items()}
        for k, v in config_dict.items():
            if hasattr(self, k) and v:
                if not getattr(self, k) or override:
                    setattr(self, k, v)

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
                    return config_file["profiles"][profile]
                else:
                    return config_file
        except FileNotFoundError as _:
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
