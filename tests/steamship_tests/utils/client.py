from contextlib import contextmanager
from typing import Any, Dict, Optional

from steamship import Configuration, Steamship, Task
from steamship.data.package.package_instance import PackageInstance
from steamship.data.plugin.plugin_instance import PluginInstance
from steamship.utils.url import Verb

TESTING_PROFILE = "test"


def get_steamship_client(fail_if_workspace_exists=False, **kwargs) -> Steamship:
    # Always use the `test` profile
    kwargs["profile"] = TESTING_PROFILE
    return Steamship(
        fail_if_workspace_exists=fail_if_workspace_exists, config=Configuration.parse_obj(kwargs)
    )


@contextmanager
def steamship_use(
    package_handle: str,
    instance_handle: str = None,
    config: Dict[str, Any] = None,
    version: str = None,
    fetch_if_exists: bool = True,
    delete_workspace: bool = True,
    **kwargs,
) -> PackageInstance:
    # Always use the `test` profile
    kwargs["profile"] = TESTING_PROFILE
    instance = Steamship.use(
        package_handle, instance_handle, config, version, fetch_if_exists, **kwargs
    )
    assert instance.client.config.workspace_id == instance.workspace_id
    yield instance
    # Clean up the workspace
    if delete_workspace:
        instance.client.get_workspace().delete()


@contextmanager
def steamship_use_as_if_deployed(klass):
    def add_method(klass, method, method_name=None):
        setattr(klass, method_name or method.__name__, method)

    def handle_kwargs(kwargs: Optional[dict] = None):
        if kwargs is not None and "wait_on_tasks" in kwargs:
            if kwargs["wait_on_tasks"] is not None:
                for task in kwargs["wait_on_tasks"]:
                    # It might not be of type Task if the invocation was something we've monkeypatched.
                    if type(task) == Task:
                        task.wait()
            kwargs.pop("wait_on_tasks")
        return kwargs

    def invoke(self, path: str, verb: Verb = Verb.POST, **kwargs):
        # Note: the correct impl would inspect the fn lookup for the fn with the right verb.
        path = path.rstrip("/").lstrip("/")
        fn = getattr(self, path)
        new_kwargs = handle_kwargs(kwargs)
        print(f"Patched invocation of self.invoke('{path}', {kwargs})")
        res = fn(**new_kwargs)
        if hasattr(res, "dict"):
            return res.dict()
        # TODO: Handle if they returned a InvocationResponse object
        return res

    def invoke_later(self, path: str, verb: Verb = Verb.POST, **kwargs):
        # Note: the correct impl would inspect the fn lookup for the fn with the right verb.
        path = path.rstrip("/").lstrip("/")
        fn = getattr(self, path)
        new_kwargs = handle_kwargs(kwargs)
        invoke_later_args = new_kwargs.get("arguments", {})  # Specific to invoke_later
        print(f"Patched invocation of self.invoke_later('{path}', {kwargs})")
        return fn(**invoke_later_args)

    client = Steamship()
    add_method(klass, invoke)
    add_method(klass, invoke_later)
    obj = klass(client=client)

    # TODO: Clean up workspace when done
    yield obj
    return obj


@contextmanager
def steamship_use_plugin(
    plugin_handle: str,
    instance_handle: str = None,
    config: Dict[str, Any] = None,
    version: str = None,
    fetch_if_exists: bool = True,
    delete_workspace: bool = True,
    **kwargs,
) -> PluginInstance:
    # Always use the `test` profile
    kwargs["profile"] = TESTING_PROFILE
    instance = Steamship.use_plugin(
        plugin_handle, instance_handle, config, version, fetch_if_exists, **kwargs
    )
    assert instance.client.config.workspace_id == instance.workspace_id
    yield instance
    # Clean up the workspace
    if delete_workspace:
        instance.client.get_workspace().delete()


@contextmanager
def steamship_use_skill(
    skill: str,
    provider: Optional[str] = None,
    instance_handle: str = None,
    fetch_if_exists: bool = True,
    delete_workspace: bool = True,
) -> PluginInstance:
    # TODO (enias): Always use the same steamship instance for testing
    instance = Steamship(profile=TESTING_PROFILE).use_skill(
        skill=skill,
        provider=provider,
        instance_handle=instance_handle,
        fetch_if_exists=fetch_if_exists,
    )
    assert instance.client.config.workspace_id == instance.workspace_id
    yield instance
    # Clean up the workspace
    if delete_workspace:
        instance.client.get_workspace().delete()


def register_plugin_instance_subclass(plugin_handle: str, plugin_class: PluginInstance):
    """Register that subclass `plugin_class` should be used for instances of plugin handle `plugin_handle`."""
    Steamship._PLUGIN_INSTANCE_SUBCLASS_OVERRIDES[plugin_handle] = plugin_class
