from __future__ import annotations

import logging
from typing import Any, Dict, List

from steamship import SteamshipError, Task
from steamship.invocable import Invocable

# Note!
# =====
#
# This the files in this package are for Package Implementors.
# If you are using the Steamship Client, you probably are looking for either steamship.client or steamship.data
#
from steamship.utils.url import Verb


class PackageService(Invocable):
    """The Abstract Base Class of a Steamship Package.

    Packages may implement whatever methods they like.  To expose these methods as invocable HTTP routes,
    annotate the method with @get or @post and the route name.

    Package *implementations* are effectively stateless, though they will have stateful

    """

    def invoke_later(
        self,
        method: str,
        verb: Verb = Verb.POST,
        wait_on_tasks: List[Task] = None,
        arguments: Dict[str, Any] = None,
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
                The keyword arguments of the invoked   method

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
        )
        return resp
