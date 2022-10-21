from __future__ import annotations

from steamship import File
from steamship.base import SteamshipError
from steamship.base.model import CamelModel
from steamship.utils.signed_urls import url_to_json


class BlockAndTagPluginInput(CamelModel):
    file: File = None

    def __init__(self, **kwargs):
        if url := kwargs.get("url"):
            # If `url` was provided, we assume that some or all of the new object's parameterization exists
            # at that location, encoded as JSON. We fetch it, parse as JSON, and fold into the kwarg dict.
            result = url_to_json(url)
            if not isinstance(result, dict):
                raise SteamshipError(
                    message=f"BlockAndTagPluginInput received a URL that resolved to {type(result)}. Needed a `dict`"
                )
            kwargs.update(result)

        super().__init__(**kwargs)
