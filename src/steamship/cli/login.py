import time
import webbrowser

import requests

from steamship.base.error import SteamshipError


def login(api_base: str, web_base: str) -> str:  # noqa: C901

    # create login token
    try:
        token_result = requests.post(api_base + "account/create_login_attempt")
        token_data = token_result.json().get("data")
    except Exception as e:
        raise SteamshipError("Could not create login token when attempting login.", error=e)

    if token_data is None:
        raise SteamshipError("Could not create login token when attempting login.")
    token = token_data.get("token")
    if token is None:
        raise SteamshipError("Could not create login token when attempting login.")

    # Launch login attempt in browser
    login_browser_url = (
        f"{web_base}account/client-login?attemptToken={token}&client=pycli&version=0.0.1"
    )
    try:
        opened_browser = webbrowser.open(login_browser_url)
    except Exception as e:
        raise SteamshipError("Exception attempting to launch browser for login.", error=e)

    if not opened_browser:
        raise SteamshipError(
            "Could not launch browser for login flow. If you are in Replit or another headless environment, please set your Steamship API key as an environment variable or in steamship.json.  See more here: https://docs.steamship.com/configuration/authentication.html"
        )

    # Wait on result
    total_poll_time = 0
    time_between_polls = 1
    api_key = None
    while total_poll_time < 300:  # Five minutes
        params = {"token": token}
        login_response = requests.post(f"{api_base}account/poll_login_attempt", json=params).json()
        if login_response.get("data", {}).get("status") == "done":
            api_key = login_response.get("data", {}).get("apiKey")
            break
        time.sleep(time_between_polls)
        total_poll_time += time_between_polls

    if api_key is None:
        raise SteamshipError("Could not fetch api key after login attempt in allotted time.")

    return api_key
