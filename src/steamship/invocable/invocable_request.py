from __future__ import annotations

from typing import Any, Dict

from steamship.base import Configuration
from steamship.base.model import CamelModel


class Invocation(CamelModel):
    http_verb: str = None
    invocation_path: str = None  # e.g. /hello/there
    arguments: Dict[str, Any] = None
    config: Dict[str, Any] = None


class LoggingConfig(CamelModel):
    logging_host: str = None
    logging_port: str = None


class InvocationContext(CamelModel):
    tenant_id: str = None
    user_id: str = None
    workspace_id: str = None
    invocable_handle: str = None
    invocable_version_handle: str = None
    invocable_instance_handle: str = None
    invocable_type: str = None
    invocable_owner_id: str = None


class InvocableRequest(CamelModel):
    """A request as the Steamship Hosting Framework receives it from the Engine.

    This class is different from the other `Request` class:
     * `steamship.base.request` represents a request from the Steamship Client
     * this class represents a request from the Steamship Engine to a Steamship-hosted App/Plugin

    It contains both a package/plugin invocation and also the client configuration in which that invocation
    is intended to execute.
    """

    client_config: Configuration = None
    invocation: Invocation = None
    logging_config: LoggingConfig = None
    invocation_context: InvocationContext = None
