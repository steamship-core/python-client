__copyright__ = "Steamship"
__license__ = "MIT"

import json
from enum import Enum

from steamship.base.model import CamelModel


class TrainingPlatform(str, Enum):
    """Note: The `str` parent object is critical for serialization!"""

    ECS = "ecs"
    LAMBDA = "lambda"


class PluginInstance(CamelModel):
    training_platform: TrainingPlatform


def test_enum_serialization_behavior():
    assert json.dumps(TrainingPlatform.ECS) == '"ecs"'

    t1 = PluginInstance.parse_obj({"training_platform": "ecs"})
    t2 = PluginInstance.parse_obj({"training_platform": "lambda"})

    assert t1.training_platform == TrainingPlatform.ECS
    assert t2.training_platform == TrainingPlatform.LAMBDA
    assert t1.training_platform == "ecs"
    assert t2.training_platform == "lambda"
