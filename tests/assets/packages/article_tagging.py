"""
THIS SHOULD BE KEPT IN SYNC WITH THE DOCS: packages/article-tagging.rst.
"""
from typing import Any, Dict, Type

from steamship import Block, File, Steamship, Tag
from steamship.invocable import Config, InvocationContext, PackageService, post


class ArticleTaggerPackage(PackageService):
    class ArticleTaggerConfig(Config):
        """Configuration required to instantiate this package."""

        labels: str  # A comma-separated list of tags to apply to articles

    def __init__(
        self, client: Steamship, config: Dict[str, Any] = None, context: InvocationContext = None
    ):
        super().__init__(client, config)

        # Instantiate a zero-shot classifier plugin
        self.classifier_instance = client.use_plugin(
            plugin_handle="zero-shot-tagger-default",
            instance_handle="my-classifier",
            config={
                "tag_kind": "tags",  # The tag.kind we want in the output
                "labels": self.config.labels,  # The labels we want to apply
                "multi_label": True,  # multi-class classification
            },
        )

    # The config_cls method allows your package to return a class
    # that defines its required configuration.
    # See Developer Reference -> Accepting Configuration
    # for more details. This package doesn't have any specific
    # required configuration, so we return the default Config object.
    @classmethod
    def config_cls(cls) -> Type[Config]:
        """Return our specific config type."""
        return cls.ArticleTaggerConfig

    # This method defines the package user's endpoint for adding content
    # The @post annotation automatically makes the method available as
    # an HTTP Post request. The name in the annotation defines the HTTP
    # route suffix, see Packages -> Package Project Structure.
    @post("add_document")
    def add_document(self, content: str, url: str) -> str:
        """Accept a new document in plaintext and start sentiment analysis"""

        # Upload the content of the file into Steamship.
        # Put the content directly into a Block, since we assume it is plaintext.
        # Create a tag with the URL so we can get it back later.
        file = File.create(
            self.client, blocks=[Block(text=content)], tags=[Tag(kind="url", name=url)]
        )

        # Tag the file with the sentiment analysis plugin
        # Using a plugin is an asynchronous call within Steamship. The
        # operation may not be complete when this method completes,
        # but that's ok. The other methods will query over whatever is
        # currently available.
        file.tag(self.classifier_instance.handle)

        return file.handle

    @staticmethod
    def _find_url(file: File):
        for tag in file.tags:
            if tag.kind == "url":
                return tag.name

    @post("documents_by_tag")
    def documents_by_tag(self, tag: str, threshold: float = 0.7) -> [str]:
        """Query the stored documents for tagged articles"""

        # Query our documents for Positive sentiment tags
        matching_files = File.query(
            self.client, f'kind "tags" and name "{tag}" and value("score") > {threshold}'
        ).files

        return [self._find_url(file) for file in matching_files]
