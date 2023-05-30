from __future__ import annotations

import logging
from functools import partial
from typing import Any, Dict, List, Optional

from steamship import SteamshipError, Task
from steamship.base.package_spec import MethodSpec
from steamship.invocable import Invocable

# Note!
# =====
#
# This the files in this package are for Package Implementors.
# If you are using the Steamship Client, you probably are looking for either steamship.client or steamship.data
#
from steamship.invocable.package_mixin import PackageMixin
from steamship.utils.url import Verb


class PackageService(Invocable):
    """The Abstract Base Class of a Steamship Package.

    Packages may implement whatever methods they like.  To expose these methods as invocable HTTP routes,
    annotate the method with @get or @post and the route name.

    Package *implementations* are effectively stateless, though they will have stateful

    """

    mixins: List[PackageMixin] = []

    def add_mixin(self, mixin: PackageMixin):
        for attribute in list(mixin.__class__.__dict__.values()):
            decorator = getattr(attribute, "decorator", None)
            if decorator:
                if getattr(decorator, "__is_endpoint__", False):
                    path = getattr(attribute, "__path__", None)
                    verb = getattr(attribute, "__verb__", None)
                    config = getattr(attribute, "__endpoint_config__", {})
                    func_binding = partial(attribute, self=mixin)
                    method_spec = MethodSpec.from_class(
                        mixin.__class__,
                        attribute.__name__,
                        path=path,
                        verb=verb,
                        config=config,
                        func_binding=func_binding,
                    )
                    self._package_spec.add_method(method_spec)
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
