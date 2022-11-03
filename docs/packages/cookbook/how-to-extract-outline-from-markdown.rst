Extract an Outline from a Markdown File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Accept a Markdown file from the remote user, convert it to text blocks using the Markdown Blockifier plugin, and then
generate an outline for the text using the tags. For example, the following Markdown file:

.. code-block:: markdown

    # This is an h1

    And some content

    ## This is an h2

    and some more content

would generate the following output:

.. code-block:: text

    This is an h1
        This is an h2

Implementation:

.. code-block:: python

    """
    This package accepts a Markdown file, extracts its text blocks
    with a Blockifier, and returns the outline of the content.
    """
    from typing import Type

    from steamship import File, MimeTypes
    from steamship.data import TagKind, DocTag
    from steamship.invocable import Config, create_handler, post, PackageService


    class MarkdownOutlinePackage(PackageService):

        # This method defines the package user's endpoint. The @post annotation
        # automatically makes the method available as an HTTP Post request.
        # The name in the annotation defines the HTTP route suffix,
        #  see Packages -> Package Project Structure.
        @post("create_markdown_outline")
        def create_markdown_outline(self, content: str = None) -> str:
            """Accept markdown content and extract its outline"""

            # Upload the content of the Markdown file into Steamship.
            file = File.create(self.client, content, mime_type=MimeTypes.MKD)

            # Now blockify it (convert it to raw text with tags) with the markdown blockifier
            blockifier = self.client.use_plugin(
                plugin_handle="markdown-blockifier-default",
                instance_handle="my-blockifier"
            )
            task = file.blockify(blockifier.handle)

            # Using a plugin is an asynchronous call within Steamship. Here we
            # assume the file is relatively short and this operation won't
            # take long, so we just wait on it within the call to the package.
            task.wait()

            # Calling file.refresh gets us the blockified results. We expect
            # one block for each element of Markdown, with a Tag telling us
            # what element type it is.
            file = file.refresh()

            # Now we build the outline.  We loop through the result blocks,
            # keeping those tagged as h[1-6].
            result_lines = []
            for block in file.blocks:
                for tag in block.tags:
                    if tag.kind == TagKind.DOCUMENT and tag.name in [
                        DocTag.H1,
                        DocTag.H2,
                        DocTag.H3,
                        DocTag.H4,
                        DocTag.H5
                    ]:
                        # Grab the numerical part of the header level, ex. 2 in "h2"
                        heading_level = int(tag.name[1:])

                        # Create indent with one fewer tab than heading level
                        heading_prefix = '\t' * (heading_level - 1)

                        # Append the block to the result, with the indent
                        result_lines.append(f"{heading_prefix}{block.text}")

            # Return the joined result
            return "\n".join(result_lines)


    # This line connects our Package implementation class to the surrounding
    # Steamship handler code.
    handler = create_handler(MarkdownOutlinePackage)

