from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar, Union

from steamship.app.response import Response
from steamship.base import Client
from steamship.base.response import SteamshipError

# Note!
# =====
#
# This the files in this package are for Plugin Implementors.
# If you are using the Steamship Client, you probably are looking for either steamship.client or steamship.data
#

T = TypeVar("T")
U = TypeVar("U")


@dataclass
class PluginRequest(Generic[T]):
    data: T = None

    @staticmethod
    def from_dict(
            d: Any,
            wrapped_object_from_dict: Callable[[dict, Client], T] = None,
            client: Client = None,
    ) -> "PluginRequest[T]":
        data = None
        if "data" in d:
            if wrapped_object_from_dict is not None:
                data = wrapped_object_from_dict(d["data"], client)
            else:
                raise SteamshipError(
                    message="No `wrapped_object_from_dict` provided to parse inbound dict request."
                )
        return PluginRequest(data=data)

    def to_dict(self) -> dict:
        if self.data is None:
            return {}
        else:
            return {"data": self.data.to_dict()}


class PluginService(ABC, Generic[T, U]):
    @abstractmethod
    def run(self, request: PluginRequest[T]) -> Union[U, Response[U]]:
        pass

    @classmethod
    def response_to_dict(cls, response: Union[SteamshipError, Response[U], U, dict]) -> Response[U]:
        try:
            if type(response) == Response:
                return response
            elif type(response) == SteamshipError:
                return Response(error=response)
            else:
                return Response(data=response)
        except SteamshipError as remote_error:
            return Response[U](error=remote_error)
        except Exception as error:
            return Response[U](
                error=SteamshipError(
                    message="Unhandled exception completing your request", error=error
                )
            )
