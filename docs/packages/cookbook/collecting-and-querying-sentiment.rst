Collecting and Querying Sentiment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This example package collects plain text files and stores them in Steamship. It runs a sentiment analysis
tagger (`OneAI Tagger <https://www.steamship.com/plugins/oneai-tagger>`_) on them as they are added.
Two endpoints allow fetching all of the positive and negative tagged documents.

..
    TODO: Test this once oneai tagger is updated

.. code-block:: python

    """
    This package accepts text documents, stores them, and runs sentiment analysis.
    """
    from typing import Type, Dict, Any

    from steamship import Block, File, Steamship
    from steamship.data import TagKind, SentimentTag
    from steamship.invocable import Config, create_handler, post, PackageService


    class SimpleSentimentPackage(PackageService):

        def __init__(self, client: Steamship, config: Dict[str, Any] = None):
            super().__init__(client, config)

            # Instantiate a sentiment plugin.
            self.sentiment_plugin_instance = client.use_plugin(
                plugin_handle="oneai-tagger",
                instance_handle="my-sentiment-analyzer",
                config={"skills": "sentiment"}
            )


        # This method defines the package user's endpoint for adding content
        # The @post annotation automatically makes the method available as
        # an HTTP Post request. The name in the annotation defines the HTTP
        # route suffix, see Packages -> Package Project Structure.
        @post("add_document")
        def add_document(self, content: str = None) -> str:
            """Accept a new document in plaintext and start sentiment analysis"""

            # Upload the content of the file into Steamship.
            # Put the content directly into a Block, since we assume it is plaintext.
            file = File.create(self.client,
                               blocks=[Block.CreateRequest(text=content)])

            # Tag the file with the sentiment analysis plugin
            # Using a plugin is an asynchronous call within Steamship. The
            # operation may not be complete when this method completes,
            # but that's ok. The other methods will query over whatever is
            # currently available.
            file.tag(self.sentiment_plugin_instance.handle)

            return file.handle

        @post("positive_sentiment_documents")
        def positive_sentiment_documents(self) -> [str]:
            """Query the stored documents for positive-sentiment"""

            # Query our documents for Positive sentiment tags
            positive_files = File.query(self.client,
                f"kind \"{TagKind.SENTIMENT}\" and name \"{SentimentTag.POSITIVE}\"").files

            return [file.blocks[0].text for file in positive_files]

        @post("negative_sentiment_documents")
        def negative_sentiment_documents(self) -> [str]:
            """Query the stored documents for negative-sentiment"""

            # Query our documents for Negative sentiment tags
            negative_files = File.query(self.client,
                f"kind \"{TagKind.SENTIMENT}\" and name \"{SentimentTag.NEGATIVE}\"").files

            return [file.blocks[0].text for file in negative_files]


    # This line connects our Package implementation class to the surrounding
    # Steamship handler code.
    handler = create_handler(SimpleSentimentPackage)





