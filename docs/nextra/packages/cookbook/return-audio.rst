Returning Audio from a Package Endpoint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Package endpoints can serve audio files by returning a ``InvocableResponse[bytes]`` object with the proper MIME Type set.

API callers will receive a binary response over HTTP with the appropriate  ``Content-Type`` header, and Steamship's auto-generated Web UI will wrap the response in an audio player widget.

.. code-block:: python

    from steamship.base.mime_types import MimeTypes
    from steamship.invocable import PackageService, get

    class AudioReturningPackage(PackageService):
        """This package demonstrates how to return audio from a Steamship package."""

        @get("audio_file")
        def audio_file(self) -> InvocableResponse[bytes]:
            _bytes = None # REPLACE: This should be a Python bytes object with MP4 Audio
            return InvocableResponse(_bytes=_bytes, mime_type=MimeTypes.MP4_AUDIO)
