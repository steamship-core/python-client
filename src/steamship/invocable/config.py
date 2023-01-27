import json
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Type, Union

from pydantic import BaseModel

from steamship.base.error import SteamshipError
from steamship.base.model import CamelModel


class ConfigParameterType(str, Enum):
    NUMBER = "number"
    STRING = "string"
    BOOLEAN = "boolean"

    @staticmethod
    def from_python_type(t: Type):
        if issubclass(t, str):
            return ConfigParameterType.STRING
        elif issubclass(t, bool):  # bool is a subclass of int, so must do this first!
            return ConfigParameterType.BOOLEAN
        elif issubclass(t, float) or issubclass(t, int):
            return ConfigParameterType.NUMBER
        else:
            raise SteamshipError(f"Unknown value type in Config: {t}")

    @staticmethod
    def parse_default_value(default_value: str, t: Type):
        if default_value is None:
            return None
        elif issubclass(t, str):
            return default_value
        elif issubclass(t, bool):  # bool is a subclass of int, so must do this first!
            return default_value == "True"
        elif issubclass(t, int):
            return int(default_value)
        elif issubclass(t, float):
            return float(default_value)
        else:
            raise SteamshipError(f"Unknown value type in Config: {t}")


class ConfigParameter(BaseModel):
    type: ConfigParameterType
    description: Optional[str] = None

    # Note order is important here in the union; Pydantic will coerce values into the first union type that fits!
    default: Optional[Union[bool, float, str]] = None


class Config(CamelModel):
    """Base class Steamship Package and Plugin configuration objects."""

    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        super().__init__(**kwargs)

    def extend_with_dict(self, d: dict, overwrite: bool = False):
        """Sets the attributes on this object with provided keys and values."""
        for key, val in (d or {}).items():
            if hasattr(self, key) and (overwrite or getattr(self, key) is None):
                setattr(self, key, val)

    def extend_with_json_file(
        self, path: Path, overwrite: bool = False, fail_on_missing_file: bool = True
    ):
        """Extends this config object's values with a JSON file from disk.

        This is useful for applying late-bound defaults, such as API keys added to a deployment bundle."""
        if not path.exists():
            if fail_on_missing_file:
                raise SteamshipError(
                    message=f"Attempted to extend Config object with {path}, but the file was not found."
                )
            return

        with open(path) as f:
            data = json.load(f)
            if not isinstance(data, dict):
                raise SteamshipError(
                    message=f"Attempted to extend Config object with {path}, but the file did not contain a JSON `dict` object."
                )
            self.extend_with_dict(data, overwrite)

    @classmethod
    def get_config_parameters(cls) -> Dict[str, ConfigParameter]:
        result = {}
        for field_name, field in cls.__fields__.items():
            description = field.field_info.description
            type_ = ConfigParameterType.from_python_type(field.type_)
            result[field_name] = ConfigParameter(
                type=type_,
                default=field.default,
                description=description,
            )

        return result
