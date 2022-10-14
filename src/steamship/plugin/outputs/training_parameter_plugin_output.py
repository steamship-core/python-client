from __future__ import annotations

from typing import Any, Dict, Optional, Type

from pydantic import BaseModel

from steamship.base.model import CamelModel
from steamship.plugin.inputs.export_plugin_input import ExportPluginInput
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput


class TrainingParameterPluginOutput(CamelModel):
    machine_type: Optional[str] = None
    training_epochs: int = None
    testing_holdout_percent: float = None
    test_split_seed: int = None
    training_params: Dict[str, Any] = None
    inference_params: Dict[str, Any] = None
    export_request: ExportPluginInput = None

    @staticmethod
    def from_input(input: TrainingParameterPluginInput) -> TrainingParameterPluginOutput:
        return TrainingParameterPluginOutput(
            export_request=input.export_plugin_input,
            training_epochs=input.training_epochs,
            testing_holdout_percent=input.testing_holdout_percent,
            test_split_seed=input.test_split_seed,
            training_params=input.training_params,
            inference_params=input.inference_params,
        )

    @classmethod
    def parse_obj(cls: Type[BaseModel], obj: Any) -> BaseModel:
        # TODO (enias): This needs to be solved at the engine side
        obj["export_request"] = obj.get("exportPluginInput")
        return super().parse_obj(obj)
