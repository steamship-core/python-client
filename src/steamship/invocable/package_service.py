from __future__ import annotations

import logging
from functools import partial
from typing import Any, Dict, List, Optional, Type

from steamship import SteamshipError, Task
from steamship.base.package_spec import MethodSpec, PackageSpec, RouteConflictError
from steamship.invocable import Invocable

# Note!
# =====
#
# This the files in this package are for Package Implementors.
# If you are using the Steamship Client, you probably are looking for either steamship.client or steamship.data
#
from steamship.invocable.invocable import find_route_methods
from steamship.invocable.package_mixin import PackageMixin
from steamship.utils.url import Verb


class PackageService(Invocable):
    """The Abstract Base Class of a Steamship Package.

    Packages may implement whatever methods they like.  To expose these methods as invocable HTTP routes,
    annotate the method with @get or @post and the route name.

    Package *implementations* are effectively stateless, though they will have stateful

    """

    USED_MIXIN_CLASSES: List[Type[PackageMixin]] = []
    mixins: List[PackageMixin]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mixins = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Now must add routes for mixins
        for used_mixin_class in cls.USED_MIXIN_CLASSES:
            mixin_qualified_name = used_mixin_class.__module__ + "." + used_mixin_class.__qualname__
            if mixin_qualified_name not in cls._package_spec.used_mixins:
                cls.scan_mixin(cls._package_spec, used_mixin_class)
                cls._package_spec.used_mixins.append(mixin_qualified_name)

    @classmethod
    def scan_mixin(
        cls,
        package_spec: PackageSpec,
        mixin_class: Type[PackageMixin],
        mixin_instance: Optional[PackageMixin] = None,
        permit_overwrite_of_existing_methods: bool = False,
    ):
        for route_method in find_route_methods(mixin_class):
            if mixin_instance is not None:
                func_binding = partial(route_method.attribute, self=mixin_instance)
            else:
                func_binding = (
                    route_method.attribute
                )  # This binding is not truly valid. It must be overwritten during add_mixin
            method_spec = MethodSpec.from_class(
                mixin_class,
                route_method.attribute.__name__,
                path=route_method.path,
                verb=route_method.verb,
                config=route_method.config,
                func_binding=func_binding,
            )
            try:
                allow_override_for_this_route = permit_overwrite_of_existing_methods
                comparison_path = (
                    route_method.path
                    if route_method.path.startswith("/")
                    else "/" + route_method.path
                )
                existing_route = package_spec.method_mappings.get(route_method.verb, {}).get(
                    comparison_path
                )
                if (
                    existing_route is not None
                    and existing_route.class_name == mixin_class.__name__
                    and mixin_instance is not None
                ):
                    allow_override_for_this_route = True
                package_spec.add_method(
                    method_spec,
                    permit_overwrite_of_existing=allow_override_for_this_route,
                )
            except RouteConflictError as conflict_error:
                message = f"When attempting to add mixin {mixin_class.__name__}, route {route_method.verb} {route_method.path} conflicted with already added route {route_method.verb} {route_method.path} on class {conflict_error.existing_method_spec.class_name}"
                raise RouteConflictError(
                    message=message,
                    existing_method_spec=conflict_error.existing_method_spec,
                )

    def add_mixin(self, mixin: PackageMixin, permit_overwrite_of_existing_methods: bool = False):
        PackageService.scan_mixin(
            self._package_spec,
            mixin.__class__,
            mixin,
            permit_overwrite_of_existing_methods=permit_overwrite_of_existing_methods,
        )
        self.mixins.append(mixin)

    def instance_init(self):
        """The instance init method will be called ONCE by the engine when a new instance of a package or plugin has been created. By default, this calls instance_init on mixins, in order."""
        for mixin in self.mixins:
            mixin.instance_init(self.config, self.context)

    def invoke_later(
        self,
        method: str,
        verb: Verb = Verb.POST,
        wait_on_tasks: List[Task] = None,
        arguments: Dict[str, Any] = None,
        delay_ms: Optional[int] = None,
    ) -> Task[Any]:
        """Schedule a method for future invocation.

        Parameters
        ----------
        method: str
                The method to invoke, as registered with Steamship in the @get or @post decorator.
        verb:   Verb
                The HTTP Verb to use. Default is POST.
        wait_on_tasks: List[Task]
                A list of Task objects (or task IDs) that should be waited upon before invocation.
        arguments: Dict[str, Any]
                The keyword arguments of the invoked method
        delay_ms: Optional[int]
                A delay, in milliseconds, before the invocation should execute.

        Returns
        -------
        Task[Any]
                A Task representing the future work
        """

        if self.context is None:
            raise SteamshipError(
                message="Unable to call invoke_later because the InvocationContext was None"
            )
        if self.context.invocable_instance_handle is None:
            raise SteamshipError(
                message="Unable to call invoke_later because the invocable_instance_handle on InvocationContext was None"
            )

        payload = {
            "instanceHandle": self.context.invocable_instance_handle,
            "payload": {
                "httpVerb": verb.value,
                "invocationPath": method,
                "arguments": arguments or {},
            },
        }
        operation = "package/instance/invoke"

        logging.info(
            f"Scheduling {verb} {method} for future invocation on me ({self.context.invocable_handle})"
        )

        resp = self.client.post(
            operation,
            payload,
            expect=Task[Task],  # This operation should return a task
            as_background_task=True,  # This operation should always be asynchronous
            wait_on_tasks=wait_on_tasks,  # This operation might await other tasks first
            task_delay_ms=delay_ms,  # This operation might have a required delay
        )
        return resp
