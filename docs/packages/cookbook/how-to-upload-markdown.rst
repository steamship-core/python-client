Upload a Markdown File
~~~~~~~~~~~~~~~~~~~~~~

Accept a Markdown File from the remote user and then Blockify it with the default Markdown Blockifier.

.. code-block:: python

   """Accept and save a file from the remote user."""
    from typing import Optional, Type

    from steamship import File, MimeTypes
    from steamship.invocable import Config, Invocable, create_handler, post, Config

    class UploadMarkdownFilePackage(Invocable):
        def config_cls(self) -> Type[Config]:
            """Return Config if your package requires no config."""
            return Config

        @post("upload_markdown_file")
        def upload_markdown_file(self, content: str = None) -> str:
            """Tokenize a Markdown text in Chinese."""
            file = File.create(self.client, content, mime_type=mime_type)

            # Now blockify it with the markdown blockifier
            blockifier = self.client.use_plugin("markdown-blockifier-default")
            task = file.blockify(blockifier.handle)
            task.wait()

            return file.id

    handler = create_handler(UploadMarkdownFilePackage)

