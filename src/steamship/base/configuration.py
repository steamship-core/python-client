import json
import os
from pathlib import Path
from typing import Dict

_configFile = '.steamship.json'


class Configuration:
    apiKey: str = None
    apiBase: str = None
    appBase: str = None
    webBase: str = None
    spaceId: str = None
    spaceHandle: str = None
    profile: str = None

    @staticmethod
    def from_dict(d: dict) -> "Configuration":
        if d is None:
            return Configuration()

        return Configuration(
            apiKey=d.get('apiKey', None),
            apiBase=d.get('apiBase', None),
            appBase=d.get('appBase', None),
            webBase=d.get('webBase', None),
            spaceId=d.get('spaceId', None),
            spaceHandle=d.get('spaceHandle', None)
        )

    def __init__(
            self,
            apiKey: str = None,
            apiBase: str = None,
            appBase: str = None,
            webBase: str = None,
            spaceId: str = None,
            spaceHandle: str = None,
            profile: str = None,
            configFile: str = None,
            configDict: dict = None,
    ):
        # First set the profile
        if "STEAMSHIP_PROFILE" in os.environ:
            self.profile = os.getenv('STEAMSHIP_PROFILE')
        if profile is not None:
            self.profile = profile

        # Then load from a file if provided
        if configFile is not None:
            self.load_from_file(configFile, self.profile)
        else:
            self.try_autofinding_files(self.profile)

        self.apply_env_var_overrides()

        if configDict is not None:
            self.merge_dict(configDict)

        self.apply_invocation_overrides(
            apiKey=apiKey,
            apiBase=apiBase,
            appBase=appBase,
            webBase=webBase,
            spaceId=spaceId,
            spaceHandle=spaceHandle
        )

        if self.apiBase is None:
            self.apiBase = 'https://api.steamship.com/api/v1/'
        if self.appBase is None:
            self.appBase = 'https://steamship.run/'
        if self.webBase is None:
            self.webBase = 'https://app.steamship.com/'

        if self.apiBase[len(self.apiBase) - 1] != '/':
            self.apiBase = "{}/".format(self.apiBase)

        if self.appBase[len(self.appBase) - 1] != '/':
            self.appBase = "{}/".format(self.appBase)

        if self.webBase[len(self.webBase) - 1] != '/':
            self.webBase = "{}/".format(self.webBase)

    def merge_dict(self, d: Dict[str, any]):
        apiKey = d.get('apiKey', None)
        if apiKey is not None:
            self.apiKey = apiKey

        apiBase = d.get('apiBase', None)
        if apiBase is not None:
            self.apiBase = apiBase

        appBase = d.get('appBase', None)
        if appBase is not None:
            self.appBase = appBase

        webBase = d.get('webBase', None)
        if webBase is not None:
            self.webBase = webBase

        profile = d.get('profile', None)
        if profile is not None:
            self.profile = profile

        spaceId = d.get('spaceId', None)
        if spaceId is not None:
            self.spaceId = spaceId

        spaceHandle = d.get('spaceHandle', None)
        if spaceHandle is not None:
            self.spaceHandle = spaceHandle

    def load_from_file(self, filepath: str, profile: str = None, throw_on_error=True):
        if not os.path.exists(filepath):
            if throw_on_error:
                raise Exception("Tried to load configuration file at {} but it did not exist.".format(filepath))
            else:
                return

        try:
            with open(filepath, 'r') as f:
                s = f.read()
                j = json.loads(s)

                if profile is None:
                    self.merge_dict(j)
                else:
                    if "profiles" not in j:
                        raise Exception("Profile {} requested but not found in {}".format(profile, filepath))
                    if profile not in j["profiles"]:
                        raise Exception("Profile {} requested but not found in {}".format(profile, filepath))
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
        MAX_DEPTH = 40
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
                self.load_from_file(filepath, profile=profile, throw_on_error=True)
                break  # Once we've found it; we're done.

    def apply_env_var_overrides(self):
        """Overrides with env vars"""
        if "STEAMSHIP_API_KEY" in os.environ:
            self.apiKey = os.getenv('STEAMSHIP_API_KEY')
        if "STEAMSHIP_API_BASE" in os.environ:
            self.apiBase = os.getenv('STEAMSHIP_API_BASE')
        if "STEAMSHIP_APP_BASE" in os.environ:
            self.appBase = os.getenv('STEAMSHIP_APP_BASE')
        if "STEAMSHIP_WEB_BASE" in os.environ:
            self.webBase = os.getenv('STEAMSHIP_WEB_BASE')
        if "STEAMSHIP_SPACE_ID" in os.environ:
            self.spaceId = os.getenv('STEAMSHIP_SPACE_ID')
        if "STEAMSHIP_SPACE_HANDLE" in os.environ:
            self.spaceHandle = os.getenv('STEAMSHIP_SPACE_HANDLE')

    def apply_invocation_overrides(
            self,
            apiKey: str = None,
            apiBase: str = None,
            appBase: str = None,
            webBase: str = None,
            spaceId: str = None,
            spaceHandle: str = None):
        if apiKey is not None:
            self.apiKey = apiKey
        if apiBase is not None:
            self.apiBase = apiBase
        if appBase is not None:
            self.appBase = appBase
        if webBase is not None:
            self.webBase = webBase
        if spaceId is not None:
            self.spaceId = spaceId
        if spaceHandle is not None:
            self.spaceHandle = spaceHandle
