.. _HowToUploadFile:

Upload a File
~~~~~~~~~~~~~

Accept a File from the remote user by creating a method that takes in the file contents as a string and
then returns its ID.

.. code-block:: python

   """Accept and save a file from the remote user."""
    from typing import Optional, Type

    from steamship import File, MimeTypes
    from steamship.invocable import Config, Invocable, create_handler, post, Config

    class UploadFilePackage(Invocable):
        def config_cls(self) -> Type[Config]:
            """Return Config if your package requires no config."""
            return Config

        @post("upload_file")
        def upload_file(self, content: str = None) -> str:
            """Tokenize a Markdown text in Chinese."""
            file = File.create(self.client, content, mime_type=mime_type)
            return file.id

    handler = create_handler(UploadFilePackage)

Accepting Binary Files
^^^^^^^^^^^^^^^^^^^^^^

If you need to accept a binary file, we suggest Base64 encoding it and passing it as a string.
