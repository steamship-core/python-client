from typing import Optional

from assets.packages.configurable_hello_world import HelloWorld

from steamship.invocable.config import Config, ConfigParameterType


def test_config_parameters():
    package = HelloWorld(
        config={
            "greeting": "yo",
            "snake_case_config": "hisss",
            "camelCaseConfig": "spit!",
            "defaultConfig": "default",
        }
    )
    config_template = package.get_config_parameters()
    assert len(config_template) == 4
    for config_param in config_template:
        assert config_param.default is None
        assert config_param.type_ == ConfigParameterType.STRING

    names = [p.name for p in config_template]
    assert "greeting" in names
    assert "snake_case_config" in names
    assert "camelCaseConfig" in names
    assert "defaultConfig" in names


def test_config_parameter_numbers():
    class NumberConfig(Config):
        x: float
        y: int

    number_config = NumberConfig(x=3, y=4)
    config_template = number_config.get_config_parameters()
    assert len(config_template) == 2
    for config_param in config_template:
        assert config_param.default is None
        assert config_param.type_ == ConfigParameterType.NUMBER

    names = [p.name for p in config_template]
    assert "x" in names
    assert "y" in names


def test_config_parameter_boolean():
    class BoolConfig(Config):
        x: bool
        y: bool

    bool_config = BoolConfig(x=True, y=False)
    config_template = bool_config.get_config_parameters()
    assert len(config_template) == 2
    for config_param in config_template:
        assert config_param.default is None
        assert config_param.type_ == ConfigParameterType.BOOLEAN

    names = [p.name for p in config_template]
    assert "x" in names
    assert "y" in names


def test_config_parameter_with_defaults():
    class DefaultsConfig(Config):
        w: str = "deeeefault"
        x: bool = True
        y: int = 3
        z: float = 7.5

    defaults_config = DefaultsConfig()
    config_template = defaults_config.get_config_parameters()
    assert len(config_template) == 4

    parameters = {p.name: p for p in config_template}
    assert parameters["w"].type_ == ConfigParameterType.STRING
    assert parameters["w"].default == "deeeefault"
    assert parameters["x"].type_ == ConfigParameterType.BOOLEAN
    assert parameters["x"].default  # Assert that the default == True
    assert parameters["y"].type_ == ConfigParameterType.NUMBER
    assert parameters["y"].default == 3
    assert parameters["z"].type_ == ConfigParameterType.NUMBER
    assert parameters["z"].default == 7.5


def test_optional_config_parameters():
    class DefaultsConfig(Config):
        w: Optional[str] = "deeeefault"
        w2: Optional[str]
        x: Optional[bool] = True
        x2: Optional[bool]
        y: Optional[int] = 3
        y2: Optional[int]
        z: Optional[float] = 7.5
        z2: Optional[float]

    defaults_config = DefaultsConfig()
    config_template = defaults_config.get_config_parameters()
    assert len(config_template) == 8

    parameters = {p.name: p for p in config_template}
    assert parameters["w"].type_ == ConfigParameterType.STRING
    assert parameters["w"].default == "deeeefault"
    assert parameters["x"].type_ == ConfigParameterType.BOOLEAN
    assert parameters["x"].default  # Assert that the default == True
    assert parameters["y"].type_ == ConfigParameterType.NUMBER
    assert parameters["y"].default == 3
    assert parameters["z"].type_ == ConfigParameterType.NUMBER
    assert parameters["z"].default == 7.5

    assert parameters["w2"].type_ == ConfigParameterType.STRING
    assert parameters["w2"].default is None
    assert parameters["x2"].type_ == ConfigParameterType.BOOLEAN
    assert parameters["x2"].default is None
    assert parameters["y2"].type_ == ConfigParameterType.NUMBER
    assert parameters["y2"].default is None
    assert parameters["z2"].type_ == ConfigParameterType.NUMBER
    assert parameters["z2"].default is None
