import json
from enum import Enum
from pathlib import Path
from typing import Dict

from steamship.base.error import SteamshipError
from steamship.base.model import CamelModel
from steamship.data.manifest import ConfigParameter, ConfigParameterType


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

    @staticmethod
    def strip_enum(default_value):
        if issubclass(type(default_value), Enum):
            return default_value.value
        else:
            return default_value

    @classmethod
    def get_config_parameters(cls) -> Dict[str, ConfigParameter]:
        result = {}
        for field_name, field in cls.__fields__.items():
            description = field.field_info.description
            type_ = ConfigParameterType.from_python_type(field.type_)
            print(field, field.required)
            default_ = cls.strip_enum(field.default)

            # Note: Pydantic treats any field with a default value as being `required == False`, which is not strictly
            # the same thing as being optional which, from the Python perspective means that "being absent is OK"
            #
            # The reason it's useful to preserve this distinction is that this metadata gets stored in the engine and
            # then used to generate user interfaces shown to an end-user.
            #
            # It is useful for that interface-generation code to have access to BOTH the status of a default value but
            # also the notion of whether the absense of a value is OK. That way it can provide hints to the user to
            # minimize surprise about how their inputs will be interpreted.
            optional_ = field.required is False and field.allow_none is True

            result[field_name] = ConfigParameter(
                type=type_, default=default_, description=description, optional=optional_
            )

        return result
