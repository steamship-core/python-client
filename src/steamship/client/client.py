from __future__ import annotations

import logging
from typing import Any, List

from steamship import Block
from steamship.base import Client, Response
from steamship.client.operations.tagger import TagRequest, TagResponse
from steamship.client.tasks import Tasks
from steamship.data import File
from steamship.data.embeddings import EmbedAndSearchRequest, EmbeddingIndex, QueryResults
from steamship.data.space import Space

_logger = logging.getLogger(__name__)


class Steamship(Client):
    """Steamship Python Client."""

    tasks: Tasks = None

    def __init__(
        self,
        api_key: str = None,
        api_base: str = None,
        app_base: str = None,
        space_id: str = None,
        space_handle: str = None,
        profile: str = None,
        config_file: str = None,
    ):
        super().__init__(
            api_key=api_key,
            api_base=api_base,
            app_base=app_base,
            space_id=space_id,
            space_handle=space_handle,
            profile=profile,
            config_file=config_file,
        )
        self.tasks = Tasks(self)

    def create_index(
        self,
        handle: str = None,
        plugin_instance: str = None,
        upsert: bool = True,
        external_id: str = None,
        external_type: str = None,
        metadata: Any = None,
        space_id: str = None,
        space_handle: str = None,
        space: Space = None,
    ) -> Response[EmbeddingIndex]:
        return EmbeddingIndex.create(
            client=self,
            handle=handle,
            plugin_instance=plugin_instance,
            upsert=upsert,
            external_id=external_id,
            external_type=external_type,
            metadata=metadata,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )

    def upload(
        self,
        filename: str = None,
        content: str = None,
        mime_type: str = None,
        space_id: str = None,
        space_handle: str = None,
        space: Space = None,
    ) -> Response[File]:
        return File.create(
            self,
            filename=filename,
            content=content,
            mime_type=mime_type,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )

    def embed_and_search(
        self,
        query: str,
        docs: List[str],
        plugin_instance: str,
        k: int = 1,
        space_id: str = None,
        space_handle: str = None,
        space: Space = None,
    ) -> Response[QueryResults]:
        req = EmbedAndSearchRequest(query=query, docs=docs, pluginInstance=plugin_instance, k=k)
        return self.post(
            "plugin/instance/embeddingSearch",
            req,
            expect=QueryResults,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )

    def tag(
        self,
        doc: str,
        plugin_instance: str = None,
        space_id: str = None,
        space_handle: str = None,
        space: Space = None,
    ) -> Response[TagResponse]:
        req = TagRequest(
            type="inline",
            file=File.CreateRequest(blocks=[Block.CreateRequest(text=doc)]),
            pluginInstance=plugin_instance,
        )
        return self.post(
            "plugin/instance/tag",
            req,
            expect=TagResponse,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )

    def for_space(self, space_id: str = None, space_handle: str = None) -> Steamship:
        """Returns a new Steamship client anchored in the provided space as its default.

        Providing either `space_id` or `space_handle` will work; both need not be provided.
        """
        client = Steamship()
        client.config = self.config.for_space(space_id=space_id, space_handle=space_handle)
        return client
