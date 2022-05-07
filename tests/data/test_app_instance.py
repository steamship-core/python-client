import base64
import os

import requests

from steamship.base.mime_types import MimeTypes
from steamship.base.tasks import TaskState
from tests.client.helpers import _steamship, deploy_app
from tests.demo_apps.demo_app import PALM_TREE_BASE_64

__copyright__ = "Steamship"
__license__ = "MIT"

def test_instance_invoke():
    palm_tree_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__),
                     '..', '..', 'test_assets', 'palm_tree.png'))

    with open(palm_tree_path, 'rb') as f:
        palm_bytes = f.read()
    base64_palm = base64.b64encode(palm_bytes).decode('utf-8')

    print(base64_palm)
    print(base64_palm.encode('ascii'))
    print(PALM_TREE_BASE_64)
    # assert(False)

    with deploy_app("demo_app.py") as (app, version, instance):
        # Now let's invoke it!
        # Note: we're invoking the data at demo_app.py in the tests/demo_apps folder
        client = _steamship()

        def get_raw(path: str):
            url = instance.full_url_for(path)
            resp = requests.get(url, headers=dict(authorization="Bearer {}".format(client.config.apiKey)))
            return resp

        res = instance.get('greet').data
        assert (res == "Hello, Person!")

        resp = get_raw("greet")
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

        # Now we test different return types
        resp_string = get_raw('resp_string')
        assert resp_string.text == "A String"

        resp_dict = get_raw('resp_dict')
        assert resp_dict.json() == dict(string="A String", int=10)

        resp_404 = get_raw('doesnt_exist')
        json_404 = resp_404.json()
        assert (isinstance(json_404, dict))
        assert (json_404.get('status', None) is not None)
        assert (json_404.get('status', None) is not None)
        assert (json_404.get('status', dict()).get('state', None) == TaskState.failed)
        assert ("No handler" in json_404.get('status', dict()).get('statusMessage', ""))
        assert (resp_404.status_code == 404)

        resp_obj = get_raw('resp_obj')
        assert resp_obj.json() == dict(name="Foo")

        resp_binary = get_raw('resp_binary')
        base64_binary = base64.b64encode(resp_binary.content).decode('utf-8')
        assert(base64_binary == base64_palm)
        assert resp_binary.headers.get('Content-Type') == MimeTypes.BINARY

        resp_bytes_io = get_raw('resp_bytes_io')
        base64_bytes_io = base64.b64encode(resp_bytes_io.content).decode('utf-8')
        assert(base64_bytes_io == base64_palm)
        assert resp_bytes_io.headers.get('Content-Type') == MimeTypes.BINARY

        resp_image = get_raw('resp_image')
        base64_image = base64.b64encode(resp_image.content).decode('utf-8')
        assert(base64_image == base64_palm)
        assert resp_image.headers.get('Content-Type') == MimeTypes.PNG
