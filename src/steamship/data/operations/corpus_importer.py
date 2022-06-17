from __future__ import annotations

from typing import Any, Dict, List

from steamship import File
from steamship.base import Client, Request, Response


class CorpusImportRequest(Request):
    # The Corpus Identifiers
    id: str = None
    handle: str = None
    type: str = "file"

    # Data for the plugin
    value: str = None
    data: str = None
    url: str = None
    plugin_instance: str = None
    file_importer_plugin_instance: str = None

    def dict(self, **kwargs) -> Dict[str, Any]:
        # TODO (enias): This can probably be bumped up the inheritance chain
        if "exclude" in kwargs:
            kwargs["exclude"] = {*(kwargs.get("exclude", set()) or set()), "client"}
        else:
            kwargs = {
                **kwargs,
                "exclude": {
                    "client",
                },
            }
        return super().dict(**kwargs)


class CorpusImportResponse(Response):
    client: Client = None
    file_import_requests: List[File.CreateRequest] = None
