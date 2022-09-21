from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

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
        workspace: str = None,
        fail_if_workspace_exists: bool = False,
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
            workspace=workspace,
            fail_if_workspace_exists=fail_if_workspace_exists,
            profile=profile,
            config_file=config_file,
            config=config,
            **kwargs,
        )
        # We use object.__setattr__ here in order to bypass Pydantic's overloading of it (which would block this
        # set unless we were to add this as a field)
        object.__setattr__(self, "use", self._instance_use)
        object.__setattr__(self, "use_plugin", self._instance_use_plugin)

    def __repr_args__(self: BaseModel) -> Any:
        """Because of the trick we've done with `use` and `use_plugin`, we need to exclude these from __repr__
        otherwise we'll get an infinite recursion."""
        return [
            (key, value)
            for key, value in self.__dict__.items()
            if key != "use" and key != "use_plugin"
        ]

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

    @staticmethod
    def use(
        package_handle: str,
        instance_handle: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        version: Optional[str] = None,
        reuse: bool = True,
        workspace_handle: Optional[str] = None,
        **kwargs,
    ) -> AppInstance:
        """Creates/loads an instance of package `package_handle`.

        The instance is named `instance_handle` and located in the Workspace named `instance_handle`.

        For example, one may write the following to always get back the same package instance, no matter how many
        times you run it, scoped into its own workspace:

        ```python
        plugin = Steamship.use('package-handle', 'instance-handle')
        ```

        If you wish to override the usage of a workspace named `instance_handle`, you can provide the `workspace_handle`
        parameter.
        """
        kwargs["workspace"] = workspace_handle or instance_handle
        client = Steamship(**kwargs)
        return client._instance_use(
            package_handle=package_handle,
            instance_handle=instance_handle,
            config=config,
            version=version,
            reuse=reuse,
        )

    def _instance_use(
        self,
        package_handle: str,
        instance_handle: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        version: Optional[str] = None,
        reuse: bool = True,
    ) -> AppInstance:
        """Creates/loads an instance of package `package_handle`.

        The instance is named `instance_handle` and located in the workspace this client is anchored to.."""
        instance = AppInstance.create(
            self,
            app_handle=package_handle,
            app_version_handle=version,
            handle=instance_handle,
            config=config,
            upsert=reuse,
        )

        if instance.error:
            raise instance.error
        if not instance.data:
            raise SteamshipError(
                f"Unable to create an instance of App {package_handle} with handle {instance_handle} in workspace {self.config.space_handle}."
            )
        return instance.data

    @staticmethod
    def use_plugin(
        plugin_handle: str,
        instance_handle: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        version: Optional[str] = None,
        reuse: bool = True,
        workspace_handle: Optional[str] = None,
        **kwargs,
    ) -> PluginInstance:
        """Creates/loads an instance of plugin `plugin_handle`.

        The instance is named `instance_handle` and located in the Workspace named `instance_handle`.

        For example, one may write the following to always get back the same plugin instance, no matter how many
        times you run it, scoped into its own workspace:

        ```python
        plugin = Steamship.use_plugin('plugin-handle', 'instance-handle')
        ```
        """
        kwargs["workspace"] = workspace_handle or instance_handle
        client = Steamship(**kwargs)
        return client._instance_use_plugin(
            plugin_handle=plugin_handle,
            instance_handle=instance_handle,
            config=config,
            version=version,
            reuse=reuse,
        )

    def _instance_use_plugin(
        self,
        plugin_handle: str,
        instance_handle: str = None,
        config: Dict[str, Any] = None,
        version: str = None,
        reuse: bool = True,
    ) -> PluginInstance:
        """Creates/loads an instance of plugin `plugin_handle`.

        The instance is named `instance_handle` and located in the workspace this client is anchored to."""
        instance = PluginInstance.create(
            self,
            plugin_handle=plugin_handle,
            plugin_version_handle=version,
            handle=instance_handle,
            config=config,
            upsert=reuse,
        )

        if instance.error:
            raise instance.error
        if not instance.data:
            raise SteamshipError(
                f"Unable to create an instance of Plugin {plugin_handle} with handle {instance_handle} in workspace {self.config.space_handle}."
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

    def get_space(self) -> Space:
        # We should probably add a hard-coded way to get this. The client in a Steamship Plugin/App comes
        # pre-configured with an API key and the Space in which this client should be operating.
        # This is a way to load the model object for that space.
        logging.info(
            f"get_space() called on client with config space {self.config.space_handle}/{self.config.space_id}"
        )
        space = Space.get(self, id_=self.config.space_id, handle=self.config.space_handle)
        if not space.data:
            logging.error("Unable to get space.")
            raise SteamshipError(
                message="Error while retrieving the Space associated with this client config.",
                internal_message=f"space_id={self.config.space_id} space_handle={self.config.space_handle}",
            )
        logging.info(f"Got space: {space.data.handle}/{space.data.id}")
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
