from __future__ import annotations

import logging
from typing import Any, Dict, List

from steamship import Block, Configuration, PluginInstance, SteamshipError
from steamship.base import Client, Response
from steamship.base.base import IResponse
from steamship.base.tasks import TaskComment, TaskCommentList
from steamship.data import File
from steamship.data.app_instance import AppInstance
from steamship.data.embeddings import EmbedAndSearchRequest, EmbeddingIndex, QueryResults
from steamship.data.operations.tagger import TagRequest, TagResponse
from steamship.data.space import Space

_logger = logging.getLogger(__name__)


class Steamship(Client):
    """Steamship Python Client."""

    def __init__(
        self,
        api_key: str = None,
        api_base: str = None,
        app_base: str = None,
        web_base: str = None,
        space_id: str = None,
        space_handle: str = None,
        create_space: bool = False,
        profile: str = None,
        config_file: str = None,
        config: Configuration = None,
        **kwargs,
    ):
        super().__init__(
            api_key=api_key,
            api_base=api_base,
            app_base=app_base,
            web_base=web_base,
            space_id=space_id,
            space_handle=space_handle,
            create_space=create_space,
            profile=profile,
            config_file=config_file,
            config=config,
        )

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
        req = EmbedAndSearchRequest(query=query, docs=docs, plugin_instance=plugin_instance, k=k)
        return self.post(
            "plugin/instance/embeddingSearch",
            req,
            expect=QueryResults,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )

    def use(
        self,
        app_handle: str,
        handle: str = None,
        config: Dict[str, Any] = None,
        version: str = None,
        reuse: bool = True,
    ) -> AppInstance:
        """Creates or loads an instance named `handle` of App named `app_handle`."""
        instance = AppInstance.create(
            self,
            app_handle=app_handle,
            app_version_handle=version,
            handle=handle,
            config=config,
            upsert=reuse,
        )

        if instance.error:
            raise instance.error
        if not instance.data:
            raise SteamshipError(
                f"Unable to create an instance of App {app_handle} with handle {handle}."
            )
        return instance.data

    def use_plugin(
        self,
        plugin_handle: str,
        handle: str = None,
        config: Dict[str, Any] = None,
        version: str = None,
        reuse: bool = True,
    ) -> PluginInstance:
        """Creates or loads an instance named `handle` of a Plugin named `plugin_handle`."""
        instance = PluginInstance.create(
            self,
            plugin_handle=plugin_handle,
            plugin_version_handle=version,
            handle=handle,
            config=config,
            upsert=reuse,
        )

        if instance.error:
            raise instance.error
        if not instance.data:
            raise SteamshipError(
                f"Unable to create an instance of Plugin {plugin_handle} with handle {handle}."
            )
        return instance.data

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
            plugin_instance=plugin_instance,
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

    def get_space(self) -> Space:
        # We should probably add a hard-coded way to get this. The client in a Steamship Plugin/App comes
        # pre-configured with an API key and the Space in which this client should be operating.
        # This is a way to load the model object for that space.
        logging.info("New client get_space")
        space = Space.get(self, id_=self.config.space_id, handle=self.config.space_handle)
        if not space.data:
            logging.error("Unable to get space.")
            raise SteamshipError(
                message="Error while retrieving the Space associated with this client config.",
                internal_message=f"space_id={self.config.space_id}   space_handle={self.config.space_handle}",
            )
        logging.info(f"Got space: {space.data.id}")
        return space.data

    def list_comments(
        self,
        task_id: str = None,
        external_id: str = None,
        external_type: str = None,
        external_group: str = None,
    ) -> IResponse[TaskCommentList]:
        return TaskComment.list(
            client=self,
            task_id=task_id,
            external_id=external_id,
            external_type=external_type,
            external_group=external_group,
        )
