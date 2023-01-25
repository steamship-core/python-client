import os
from enum import Enum

from steamship.base.configuration import Configuration
from steamship.base.error import SteamshipError


class RuntimeEnvironments(str, Enum):
    REPLIT = "replit"
    LOCALHOST = "localhost"


def _interactively_get_key(env: RuntimeEnvironments):
    print(
        """Get your free API key here: https://steamship.com/account/api

You'll get immediate access to our SDK for AI models, including OpenAI, GPT, Cohere, and more.
"""
    )

    api_key = input("Paste your API key to run: ")

    while len(api_key.strip()) == 0:
        api_key = input("API Key: ")

    os.environ["STEAMSHIP_API_KEY"] = api_key

    if env == RuntimeEnvironments.REPLIT:
        print(
            """
This key is set temporarily. In the future, you can:
- Set the STEAMSHIP_API_KEY Replit Secret
- Close and re-open any Replit shells to make sure secrets are refreshed.

"""
        )
    elif env == RuntimeEnvironments.LOCALHOST:
        print(
            """
This key is set temporarily. In the future, you can:
- Set the STEAMSHIP_API_KEY environment variable
- Run `ship login` to create a ~/.steamship.json credential file

"""
        )


def _report_error_and_exit(env: RuntimeEnvironments):
    if env == RuntimeEnvironments.REPLIT:
        print(
            """To run this Replit, you will need a Steamship API Key.

1) If you're viewing someone else's Replit, clone it

2) Visit https://steamship.com/account/api to get a key

3) Add your key as a Replit secret named STEAMSHIP_API_KEY

4) Close and re-open any shells to make sure your new secret is available

Then try running again!"""
        )
    elif env == RuntimeEnvironments.LOCALHOST:
        print(
            """To run this script, you will need a Steamship API Key.

1) Visit https://steamship.com/account/api to get a key

2) Set your key as the environment variable STEAMSHIP_API_KEY

Then try running again!

If you have pip-installed `steamship`, you can also try setting your key by simply running `ship login`.
"""
        )
    exit(-1)


def check_environment(env: RuntimeEnvironments, interactively_set_key: bool = True):
    # This will try loading from STEAMSHIP_API_KEY and also ~/.steamship.json
    try:
        config = Configuration()

        # If an API key is set, we're good to go!
        if config.api_key:
            return
    except SteamshipError:
        # The Configuration object will throw an error if there is no API Key found.
        # Since that error is expected from the context of this function, we pass on it to handle it in a more
        # user-interactive way.
        pass

    # If we're hot-loading config, do it here!
    if interactively_set_key:
        _interactively_get_key(env)
        return

    # If we're still here, we're not interactively setting the key. Display an error message and exit.
    _report_error_and_exit(env)
