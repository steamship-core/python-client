import sys

from steamship import Steamship
from steamship.base.configuration import Configuration
from steamship.data.user import User


def cli():
    if len(sys.argv) != 2 or sys.argv[1] not in ["login", "deploy"]:
        print("Only options are login or deploy.")
        sys.exit(-1)
    else:
        print("Logging into Steamship.")
        if sys.argv[1] == "login":
            if Configuration.default_config_file_has_api_key():
                response = input(
                    "You already have an API key in your .steamship.json file.  Do you want to remove it and login? [y/n] "
                )
                if response.lower() != "y":
                    sys.exit(0)
                Configuration.remove_api_key_from_default_config()

            # Carry on with login
            client = Steamship()
            user = User.current(client)
            print(f"🚢🚢🚢 Hooray! You're logged in with user handle: {user.handle} 🚢🚢🚢")
