from enum import Enum
from typing import Optional

from steamship.invocable import InvocableResponse, PackageService, post


class DropdownValue(str, Enum):
    VALUE1 = "value1"
    VALUE2 = "value2"


class OptionalParams(PackageService):
    @post("enum_route")
    def enum_route(
        self, dropdown_value: Optional[DropdownValue] = DropdownValue.VALUE1
    ) -> InvocableResponse:
        return InvocableResponse(string=f"You picked {dropdown_value}")
