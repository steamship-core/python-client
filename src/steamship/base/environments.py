import os
from enum import Enum


class RuntimeEnvironments(str, Enum):
    REPLIT = "replit"
    LOCALHOST = "localhost"


def check_environment(env: RuntimeEnvironments, exit_unless_key: bool = True):
    api_key = os.environ.get("STEAMSHIP_API_KEY")

    if not api_key:
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
        if exit_unless_key:
            exit(-1)
