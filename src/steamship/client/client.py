from __future__ import annotations

import logging
from typing import Any, Dict, List

from steamship import Configuration, SteamshipError
from steamship.base import Client, Response
from steamship.client.tasks import Tasks
from steamship.data import File
from steamship.data.app import App
from steamship.data.app_instance import AppInstance
from steamship.data.embeddings import EmbedAndSearchRequest, EmbeddingIndex, QueryResults
from steamship.data.space import Space

_logger = logging.getLogger(__name__)


class Steamship(Client):
    """Steamship Python Client."""

    tasks: Tasks = None  # TODO (enias): Ignore during serialisation

    def __init__(
        self,
        api_key: str = None,
        api_base: str = None,
        app_base: str = None,
        space_id: str = None,
        space_handle: str = None,
        profile: str = None,
        config_file: str = None,
        config: Configuration = None,
        **kwargs,
    ):
        super().__init__(
            api_key=api_key,
            api_base=api_base,
            app_base=app_base,
            space_id=space_id,
            space_handle=space_handle,
            profile=profile,
            config_file=config_file,
            config=config,
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
        self, app_handle: str, handle: str = None, config: Dict[str, Any] = None
    ) -> AppInstance:
        """Convenience function for creating or loading an instance of an app."""

        # TODO: The Engine API should permit App Handles to avoid having this extra round trip.
        app = App.get(client=self, handle=app_handle)
        if app.error:
            raise app.error
        if not app.data:
            raise SteamshipError(f"A Steamship App with handle {app_handle} was not found.")

        instance = AppInstance.create(
            client=self, app_id=app.data.id, handle=handle, upsert=True, config=config
        )
        if instance.error:
            raise instance.error
        if not instance.data:
            raise SteamshipError(
                f"Unable to create an instance of App {app_handle} with handle {handle}."
            )

        return instance.data

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
            logging.error(f"Unable to get space.")
            raise SteamshipError(
                message="Error while retrieving the Space associated with this client config.",
                internal_message=f"space_id={self.config.space_id}   space_handle={self.config.space_handle}",
            )
        logging.info(f"Got space: {space.data.id}")
        return space.data
