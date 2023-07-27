Returning an Image from a Package Endpoint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Package endpoints can serve images by returning a ``InvocableResponse[bytes]`` object with the proper MIME Type set.

API callers will receive a binary response over HTTP with the appropriate  ``Content-Type`` header, and Steamship's auto-generated Web UI will convert the response to an image in the browser.

.. code-block:: python

    from steamship.base.mime_types import MimeTypes
    from steamship.invocable import PackageService, get

    class ImageReturningSteamshipPackage(PackageService):
        """This package demonstrates how to return an image from a Steamship package."""

        @get("image_file")
        def image_file(self) -> InvocableResponse[bytes]:
            _bytes = None # REPLACE: This should be a Python bytes object with a PNG image
            return InvocableResponse(_bytes=_bytes, mime_type=MimeTypes.PNG)
