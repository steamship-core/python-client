__copyright__ = "Steamship"
__license__ = "MIT"

import json
from enum import Enum

from pydantic import BaseModel


class TrainingPlatform(str, Enum):
    """Note: The `str` parent object is critical for serialization!"""

    ECS = "ecs"
    LAMBDA = "lambda"


class PluginInstance(BaseModel):
    training_platform: TrainingPlatform

    @staticmethod
    def from_dict(d: dict):
        return PluginInstance(training_platform=d.get("training_platform"))


def test_enum_serialization_behavior():
    assert json.dumps(TrainingPlatform.ECS) == '"ecs"'

    t1 = PluginInstance.from_dict({"training_platform": "ecs"})
    t2 = PluginInstance.from_dict({"training_platform": "lambda"})

    assert t1.training_platform == TrainingPlatform.ECS
    assert t2.training_platform == TrainingPlatform.LAMBDA
    assert t1.training_platform == "ecs"
    assert t2.training_platform == "lambda"
    assert str(t2.training_platform) == "lambda"
