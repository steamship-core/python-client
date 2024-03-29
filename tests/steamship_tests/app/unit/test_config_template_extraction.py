from typing import Optional

from assets.packages.configurable_hello_world import HelloWorld
from pydantic import Field

from steamship.invocable.config import Config, ConfigParameterType


def test_config_parameters():
    config_template = HelloWorld.get_config_parameters()
    assert len(config_template) == 4
    for config_param in config_template.values():
        assert config_param.default is None
        assert config_param.type == ConfigParameterType.STRING

    names = config_template.keys()
    assert "greeting" in names
    assert "snake_case_config" in names
    assert "camelCaseConfig" in names
    assert "defaultConfig" in names


def test_config_parameter_numbers():
    class NumberConfig(Config):
        x: float
        y: int

    config_template = NumberConfig.get_config_parameters()
    assert len(config_template) == 2
    for config_param in config_template.values():
        assert config_param.default is None
        assert config_param.type == ConfigParameterType.NUMBER

    names = config_template.keys()
    assert "x" in names
    assert "y" in names


def test_config_parameter_boolean():
    class BoolConfig(Config):
        x: bool
        y: bool

    bool_config = BoolConfig(x=True, y=False)
    config_template = bool_config.get_config_parameters()
    assert len(config_template) == 2
    for config_param in config_template.values():
        assert config_param.default is None
        assert config_param.type == ConfigParameterType.BOOLEAN

    names = config_template.keys()
    assert "x" in names
    assert "y" in names

    # assert config_template["x"].optional is False
    # assert config_template["y"].optional is False


def test_config_parameter_with_defaults():
    class DefaultsConfig(Config):
        w: str = "deeeefault"
        x: bool = True
        y: int = 3
        z: float = 7.5

    defaults_config = DefaultsConfig()
    config_template = defaults_config.get_config_parameters()
    assert len(config_template) == 4

    assert config_template["w"].type == ConfigParameterType.STRING
    assert config_template["w"].default == "deeeefault"
    # assert config_template["w"].optional is False
    assert config_template["x"].type == ConfigParameterType.BOOLEAN
    assert config_template["x"].default  # Assert that the default == True
    # assert config_template["x"].optional is False
    assert config_template["y"].type == ConfigParameterType.NUMBER
    assert config_template["y"].default == 3
    # assert config_template["y"].optional is False
    assert config_template["z"].type == ConfigParameterType.NUMBER
    assert config_template["z"].default == 7.5
    # assert config_template["z"].optional is False


def test_optional_config_parameters():
    class DefaultsConfig(Config):
        w: Optional[str] = "deeeefault"
        w2: Optional[str]
        w3: Optional[str] = None
        x: Optional[bool] = True
        x2: Optional[bool]
        x3: Optional[bool] = None
        y: Optional[int] = 3
        y2: Optional[int]
        y3: Optional[int] = None
        z: Optional[float] = 7.5
        z2: Optional[float]
        z3: Optional[float] = None

    defaults_config = DefaultsConfig()
    config_template = defaults_config.get_config_parameters()
    assert len(config_template) == 12

    assert config_template["w"].type == ConfigParameterType.STRING
    assert config_template["w"].default == "deeeefault"
    # assert config_template["w"].optional
    assert config_template["x"].type == ConfigParameterType.BOOLEAN
    assert config_template["x"].default  # Assert that the default == True
    # assert config_template["x"].optional
    assert config_template["y"].type == ConfigParameterType.NUMBER
    assert config_template["y"].default == 3
    # assert config_template["y"].optional
    assert config_template["z"].type == ConfigParameterType.NUMBER
    assert config_template["z"].default == 7.5
    # assert config_template["z"].optional

    assert config_template["w2"].type == ConfigParameterType.STRING
    assert config_template["w2"].default is None
    # assert config_template["w2"].optional
    assert config_template["x2"].type == ConfigParameterType.BOOLEAN
    assert config_template["x2"].default is None
    # assert config_template["x2"].optional
    assert config_template["y2"].type == ConfigParameterType.NUMBER
    assert config_template["y2"].default is None
    # assert config_template["y2"].optional
    assert config_template["z2"].type == ConfigParameterType.NUMBER
    assert config_template["z2"].default is None
    # assert config_template["z2"].optional

    assert config_template["w3"].type == ConfigParameterType.STRING
    assert config_template["w3"].default is None
    # assert config_template["w3"].optional
    assert config_template["x3"].type == ConfigParameterType.BOOLEAN
    assert config_template["x3"].default is None
    # assert config_template["x3"].optional
    assert config_template["y3"].type == ConfigParameterType.NUMBER
    assert config_template["y3"].default is None
    # assert config_template["y3"].optional
    assert config_template["z3"].type == ConfigParameterType.NUMBER
    assert config_template["z3"].default is None
    # assert config_template["z3"].optional


def test_descriptions():
    class DescriptionConfig(Config):
        x: int = Field(description="Test Description")

    description_config = DescriptionConfig(x=3)
    config_template = description_config.get_config_parameters()
    assert len(config_template) == 1

    # TODO: descriptions
    assert config_template["x"].description == "Test Description"
