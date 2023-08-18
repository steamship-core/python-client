from pydantic import Field

from steamship.invocable import Config


class MixinConfig1(Config):
    field_1: str = Field(description="Some field")


class MixinConfig2(Config):
    field_2: str = Field(description="Some field")


class PackageConfig(MixinConfig1, MixinConfig2):
    def __init__(self, **kwargs):
        MixinConfig1().__init__(**kwargs)
        MixinConfig2().__init__(**kwargs)


def test_multi_inheritance():
    pc = PackageConfig.parse_obj({"field_1": "field_1", "field_2": "field_1"})
    assert pc.field1
    assert pc.field2
