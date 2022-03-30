import requests

from steamship.data.user import User
from tests.client.helpers import _steamship, deploy_app, shouldUseSubdomain

__copyright__ = "Steamship"
__license__ = "MIT"


def test_instance_invoke():
    with deploy_app("demo_app.py") as (app, version, instance):
        # Now let's invoke it!
        # Note: we're invoking the data at demo_app.py in the tests/demo_apps folder
        client = _steamship()
        res = instance.get('greet').data
        assert (res == "Hello, Person!")

        useSubdomain = shouldUseSubdomain(client)

        # Also try with raw http
        user = User.current(client).data
        url = instance.full_url_for("greet")
        resp = requests.get(url, headers=dict(authorization="Bearer {}".format(client.config.apiKey)))
        assert (resp.text == "Hello, Person!")

        res = instance.get('greet', name="Ted").data
        assert (res == "Hello, Ted!")
        url = instance.full_url_for("greet?name=Ted")
        resp = requests.get(url, headers=dict(authorization="Bearer {}".format(client.config.apiKey)))
        assert (resp.text == "Hello, Ted!")

        res = instance.post('greet').data
        assert (res == "Hello, Person!")
        url = instance.full_url_for("greet")
        resp = requests.post(url, headers=dict(authorization="Bearer {}".format(client.config.apiKey)))
        assert (resp.text == "Hello, Person!")

        res = instance.post('greet', name="Ted").data
        assert (res == "Hello, Ted!")
        url = instance.full_url_for("greet")
        resp = requests.post(url, json=dict(name="Ted"),
                             headers=dict(authorization="Bearer {}".format(client.config.apiKey)))
        assert (resp.text == "Hello, Ted!")
