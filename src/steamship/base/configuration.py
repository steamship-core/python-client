from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel

_configFile = ".steamship.json"

MAX_DEPTH = 40


class Configuration(BaseModel):
    api_key: str = None
    api_base: str = None
    app_base: str = None
    web_base: str = None
    space_id: str = None
    space_handle: str = None
    profile: Optional[str] = None

    @staticmethod
    def from_dict(d: dict) -> Configuration:
        if d is None:
            return Configuration()

        return Configuration(
            api_key=d.get("apiKey"),
            api_base=d.get("apiBase"),
            app_base=d.get("appBase"),
            web_base=d.get("webBase"),
            space_id=d.get("spaceId"),
            space_handle=d.get("spaceHandle"),
        )

    def __init__(
        self,
        api_key: str = None,
        api_base: str = None,
        app_base: str = None,
        web_base: str = None,
        space_id: str = None,
        space_handle: str = None,
        profile: str = None,
        config_file: str = None,
        config_dict: dict = None,
    ):
        super().__init__()
        # First set the profile
        if "STEAMSHIP_PROFILE" in os.environ:
            self.profile = os.getenv("STEAMSHIP_PROFILE")
        if profile is not None:
            self.profile = profile

        # Then load from a file if provided
        if config_file is not None:
            self.load_from_file(config_file, self.profile)
        else:
            self.try_autofinding_files(self.profile)

        self.apply_env_var_overrides()

        if config_dict is not None:
            self.merge_dict(config_dict)

        self.apply_invocation_overrides(
            api_key=api_key,
            api_base=api_base,
            app_base=app_base,
            web_base=web_base,
            space_id=space_id,
            space_handle=space_handle,
        )

        if self.api_base is None:
            self.api_base = "https://api.steamship.com/api/v1/"
        if self.app_base is None:
            self.app_base = "https://steamship.run/"
        if self.web_base is None:
            self.web_base = "https://app.steamship.com/"

        if self.api_base[len(self.api_base) - 1] != "/":
            self.api_base = f"{self.api_base}/"

        if self.app_base[len(self.app_base) - 1] != "/":
            self.app_base = f"{self.app_base}/"

        if self.web_base[len(self.web_base) - 1] != "/":
            self.web_base = f"{self.web_base}/"

    def merge_dict(self, d: Dict[str, Any]):
        api_key = d.get("apiKey")
        if api_key is not None:
            self.api_key = api_key

        api_base = d.get("apiBase")
        if api_base is not None:
            self.api_base = api_base

        app_base = d.get("appBase")
        if app_base is not None:
            self.app_base = app_base

        web_base = d.get("webBase")
        if web_base is not None:
            self.web_base = web_base

        profile = d.get("profile")
        if profile is not None:
            self.profile = profile

        space_id = d.get("spaceId")
        if space_id is not None:
            self.space_id = space_id

        space_handle = d.get("spaceHandle")
        if space_handle is not None:
            self.space_handle = space_handle

    def load_from_file(self, filepath: str, profile: str = None, throw_on_error=True):
        if not os.path.exists(filepath):
            if throw_on_error:
                raise Exception(
                    f"Tried to load configuration file at {filepath} but it did not exist."
                )
            else:
                return

        try:
            with open(filepath, "r") as f:
                s = f.read()
                j = json.loads(s)

                if profile is None:
                    self.merge_dict(j)
                else:
                    if "profiles" not in j or profile not in j["profiles"]:
                        raise Exception(f"Profile {profile} requested but not found in {filepath}")
                    self.merge_dict(j["profiles"][profile])

        except Exception as err:
            if throw_on_error:
                raise err
            return

    def try_autofinding_files(self, profile: str = None):
        """
        Tries folders from cwd up to root.
        """
        paths = []
        cwd = Path(os.getcwd()).absolute()
        i = 0
        while len(str(cwd)) > 0 and str(cwd) != os.path.sep:
            paths.append(os.path.join(cwd, _configFile))
            cwd = cwd.parent.absolute()
            i += 1
            if i > MAX_DEPTH:
                print("ERROR: Max depth exceeded in config search recursion.")
                break

        paths.append(os.path.join(str(Path.home()), _configFile))
        for filepath in paths:
            if os.path.exists(filepath):
                self.load_from_file(filepath, profile=profile)
                break  # Once we've found it; we're done.

    def apply_env_var_overrides(self):
        """Overrides with env vars"""
        if "STEAMSHIP_API_KEY" in os.environ:
            self.api_key = os.getenv("STEAMSHIP_API_KEY")
        if "STEAMSHIP_API_BASE" in os.environ:
            self.api_base = os.getenv("STEAMSHIP_API_BASE")
        if "STEAMSHIP_APP_BASE" in os.environ:
            self.app_base = os.getenv("STEAMSHIP_APP_BASE")
        if "STEAMSHIP_WEB_BASE" in os.environ:
            self.web_base = os.getenv("STEAMSHIP_WEB_BASE")
        if "STEAMSHIP_SPACE_ID" in os.environ:
            self.space_id = os.getenv("STEAMSHIP_SPACE_ID")
        if "STEAMSHIP_SPACE_HANDLE" in os.environ:
            self.space_handle = os.getenv("STEAMSHIP_SPACE_HANDLE")

    def apply_invocation_overrides(
        self,
        api_key: str = None,
        api_base: str = None,
        app_base: str = None,
        web_base: str = None,
        space_id: str = None,
        space_handle: str = None,
    ):
        if api_key is not None:
            self.api_key = api_key
        if api_base is not None:
            self.api_base = api_base
        if app_base is not None:
            self.app_base = app_base
        if web_base is not None:
            self.web_base = web_base
        if space_id is not None:
            self.space_id = space_id
        if space_handle is not None:
            self.space_handle = space_handle
