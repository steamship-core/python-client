from __future__ import annotations

from typing import Any, Dict, Optional, Type

from pydantic import BaseModel

from steamship.base.configuration import CamelModel
from steamship.plugin.inputs.export_plugin_input import ExportPluginInput


class TrainingParameterPluginOutput(CamelModel):
    machine_type: Optional[str] = None
    training_epochs: int = None
    testing_holdout_percent: float = None
    test_split_seed: int = None
    training_params: Dict[str, Any] = None
    inference_params: Dict[str, Any] = None
    export_request: ExportPluginInput = None

    @classmethod
    def parse_obj(cls: Type[BaseModel], obj: Any) -> BaseModel:
        # TODO (enias): This needs to be solved at the engine side
        obj["export_request"] = obj.get("exportPluginInput")
        return super().parse_obj(obj)
