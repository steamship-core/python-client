import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar, Generic, Union, Callable

from steamship.base import Client
from steamship.base.response import RemoteError, Task

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
                raise RemoteError(
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
    error: RemoteError = None
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
            error = RemoteError.from_dict(d["error"], client=client)
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
    def _run(self, request: PluginRequest[T]) -> Union[U, PluginResponse[U]]:
        pass

    @classmethod
    @abstractmethod
    def subclass_request_from_dict(cls, d: any, client: Client = None) -> PluginRequest[T]:
        pass

    def run(self, request: Union[PluginRequest[T], dict]) -> PluginResponse[U]:
        if type(request) == dict:
            try:
                request = PluginRequest[T].from_dict(
                    request,
                    subclass_request_from_dict=self.__class__.subclass_request_from_dict
                )
            except Exception as error:
                return PluginResponse[U](error=RemoteError(
                    message="Unable to parse input request.",
                    error=error
                ))
        try:
            ret = self._run(request)
            if type(ret) == PluginResponse:
                return ret
            elif type(ret) == U:
                return PluginResponse(data=ret)
            elif type(ret) == RemoteError:
                return PluginResponse(error=ret)
            else:
                logging.warning("An unexpected response type ({}) was found.".format(type(ret)))
                return PluginResponse(data=ret)
        except RemoteError as remote_error:
            return PluginResponse[U](error=remote_error)
        except Exception as error:
            return PluginResponse[U](error=RemoteError(
                message="Unhandled exception completing your request",
                error=error
            ))
