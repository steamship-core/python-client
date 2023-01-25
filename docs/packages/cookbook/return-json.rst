Returning JSON data from a Package Endpoint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Package endpoints can serve JSON data by returning a python ``dict`` object from a method.

API callers will receive a JSON response over HTTP with the appropriate  ``Content-Type`` header, and Steamship's auto-generated Web UI will convert the JSON response to a formatted web view.

.. code-block:: python

    from steamship.invocable import PackageService, get

    class JsonReturningSteamshipPackage(PackageService):
        """This package demonstrates how to return a JSON object from a Steamship package."""

        @get("json_object")
        def json_object(self) -> dict:
            return {
                "greeting": "Hello, world!"
            }
