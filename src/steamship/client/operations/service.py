from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar, Generic, Union, Callable

from steamship.base import Client
from steamship.base.response import SteamshipError, Task

T = TypeVar('T')
U = TypeVar('U')


@dataclass
class PluginRequest(Generic[T]):
    data: T = None

    @staticmethod
    def from_dict(
            d: any,
            subclass_request_from_dict: Callable[[dict, Client], dict] = None,
            client: Client = None
    ) -> "PluginRequest(Generic[T])":
        data = None
        if "data" in d:
            if subclass_request_from_dict is not None:
                data = subclass_request_from_dict(d["data"], client=client)
            else:
                raise SteamshipError(
                    message="No `subclass_request_from_dict` provided to parse inbound dict request."
                )
        return PluginRequest(data=data)

    def to_dict(self) -> dict:
        if self.data is None:
            return dict()
        else:
            return dict(data=self.data.to_dict())


@dataclass
class PluginResponse(Generic[U]):
    error: SteamshipError = None
    task: Task[U] = None
    data: U = None

    @staticmethod
    def from_dict(
            d: any,
            client: Client = None
    ) -> "PluginResponse(Generic[U])":
        data = None
        error = None
        task = None

        if "data" in d:
            data = d["data"].to_dict()
        if "error" in d:
            error = SteamshipError.from_dict(d["error"], client=client)
        if "task" in d:
            task = Task[U].from_dict(d["task"], client=client)

        return PluginResponse(data=data, task=task, error=error)

    def to_dict(self) -> dict:
        return dict(
            data=None if self.data is None else self.data.to_dict(),
            error=None if self.error is None else self.error.to_dict(),
            task=None if self.task is None else self.task.to_dict()
        )


class PluginService(ABC, Generic[T, U]):
    @abstractmethod
    def run(self, request: PluginRequest[T]) -> Union[U, PluginResponse[U]]:
        pass

    @classmethod
    @abstractmethod
    def subclass_request_from_dict(cls, d: any, client: Client = None) -> PluginRequest[T]:
        pass

    @classmethod
    def parse_request(cls, request: Union[PluginRequest[T], dict]) -> PluginRequest[T]:
        if type(request) == dict:
            try:
                request = PluginRequest[T].from_dict(
                    request,
                    subclass_request_from_dict=cls.subclass_request_from_dict
                )
            except Exception as error:
                raise SteamshipError(
                    message="Unable to parse input request.",
                    error=error
                )
        return request

    @classmethod
    def response_to_dict(cls, response: Union[SteamshipError, PluginResponse[U], U, dict]) -> PluginResponse[U]:
        try:
            if type(response) == PluginResponse:
                return response
            elif type(response) == SteamshipError:
                return PluginResponse(error=response)
            else:
                return PluginResponse(data=response)
        except SteamshipError as remote_error:
            return PluginResponse[U](error=remote_error)
        except Exception as error:
            return PluginResponse[U](error=SteamshipError(
                message="Unhandled exception completing your request",
                error=error
            ))
