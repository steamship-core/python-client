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
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput
from steamship.plugin.outputs.training_parameter_plugin_output import TrainingParameterPluginOutput

T = TypeVar("T")
U = TypeVar("U")


@dataclass
class PluginRequest(Generic[T]):
    data: T = None

    @staticmethod
    def from_dict(
        d: Any,
        subclass_request_from_dict: Callable[[dict, Client], dict] = None,
        client: Client = None,
    ) -> "PluginRequest[T]":
        data = None
        if "data" in d:
            if subclass_request_from_dict is not None:
                data = subclass_request_from_dict(d["data"], client)
            else:
                raise SteamshipError(
                    message="No `subclass_request_from_dict` provided to parse inbound dict request."
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
        """Runs the core operation implemented by this plugin: import, export, blockify, tag, etc."""
        pass

    def get_training_parameters(self, request: PluginRequest[TrainingParameterPluginInput]) -> Response[TrainingParameterPluginOutput]:
        """Produces the training parameters for this plugin.

        - If the plugin is not trainable, the subclass simply doesn't override this method.
        - If the plugin is trainable, this gives the hard-coded plugin implementation an opportunity to refine
          any training parameters supplied by the end-user before training begins.
        """
        raise SteamshipError(
            message="get_training_parameters has not been implemented on this plugin."
        )

    def train(self, request: PluginRequest[TrainingParameterPluginInput]) -> Response[TrainingParameterPluginOutput]:
        """Produces the training parameters for this plugin.

        - If the plugin is not trainable, the subclass simply doesn't override this method.
        - If the plugin is trainable, this gives the hard-coded plugin implementation an opportunity to refine
          any training parameters supplied by the end-user before training begins.
        """
        raise SteamshipError(
            message="get_training_parameters has not been implemented on this plugin."
        )

    @classmethod
    @abstractmethod
    def subclass_request_from_dict(
        cls, d: Any, client: Client = None
    ) -> PluginRequest[T]:
        pass

    @classmethod
    def parse_request(cls, request: Union[PluginRequest[T], dict]) -> PluginRequest[T]:
        if type(request) == dict:
            try:
                request = PluginRequest[T].from_dict(
                    request, subclass_request_from_dict=cls.subclass_request_from_dict
                )
            except Exception as error:
                raise SteamshipError(
                    message="Unable to parse input request.", error=error
                )
        return request

    @classmethod
    def response_to_dict(
        cls, response: Union[SteamshipError, Response[U], U, dict]
    ) -> Response[U]:
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
