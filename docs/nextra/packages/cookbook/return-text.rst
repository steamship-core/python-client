Returning text data from a Package Endpoint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Package endpoints can serve text data by returning a python ``str`` object from a method.

API callers will receive plain text response over HTTP with the appropriate  ``Content-Type`` header, and Steamship's auto-generated Web UI will convert the text response to a formatted web view and interpret it as Markdown.

.. code-block:: python

    from steamship.invocable import PackageService, get

    class TextReturningSteamshipPackage(PackageService):
        """This package demonstrates how to return a text object from a Steamship package."""

        @get("text_object")
        def text_object(self) -> str:
            return "Hello, world!"
