from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from steamship import Configuration, PackageInstance, PluginInstance, SteamshipError, Workspace
from steamship.base.client import Client
from steamship.data.embeddings import EmbedAndSearchRequest, QueryResults

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
        trust_workspace_config: bool = False,  # For use by lambda_handler; don't fetch the workspace
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
            trust_workspace_config=trust_workspace_config,
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

    def embed_and_search(
        self,
        query: str,
        docs: List[str],
        plugin_instance: str,
        k: int = 1,
    ) -> QueryResults:
        req = EmbedAndSearchRequest(query=query, docs=docs, plugin_instance=plugin_instance, k=k)
        return self.post(
            "plugin/instance/embeddingSearch",
            req,
            expect=QueryResults,
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
    ) -> PackageInstance:
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
    ) -> PackageInstance:
        """Creates/loads an instance of package `package_handle`.

        The instance is named `instance_handle` and located in the workspace this client is anchored to.."""
        instance = PackageInstance.create(
            self,
            package_handle=package_handle,
            package_version_handle=version,
            handle=instance_handle,
            config=config,
            fetch_if_exists=reuse,
        )

        return instance

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
            fetch_if_exists=reuse,
        )

        return instance

    def get_workspace(self) -> Workspace:
        # We should probably add a hard-coded way to get this. The client in a Steamship Plugin/App comes
        # pre-configured with an API key and the Workspace in which this client should be operating.
        # This is a way to load the model object for that workspace.
        logging.info(
            f"get_workspace() called on client with config workspace {self.config.workspace_handle}/{self.config.workspace_id}"
        )
        workspace = Workspace.get(
            self, id_=self.config.workspace_id, handle=self.config.workspace_handle
        )
        if not workspace:
            logging.error("Unable to get workspace.")
            raise SteamshipError(
                message="Error while retrieving the Workspace associated with this client config.",
                internal_message=f"workspace_id={self.config.workspace_id} workspace_handle={self.config.workspace_handle}",
            )
        logging.info(f"Got workspace: {workspace.handle}/{workspace.id}")
        return workspace
