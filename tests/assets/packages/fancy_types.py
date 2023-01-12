from enum import Enum

from steamship.invocable import InvocableResponse, PackageService, longstr, post


class DropdownValue(str, Enum):
    VALUE1 = "value1"
    VALUE2 = "value2"


class FancyTypes(PackageService):
    @post("enum_route")
    def enum_route(self, dropdown_value: DropdownValue) -> InvocableResponse:
        return InvocableResponse(string=f"You picked {dropdown_value}")

    @post("long_string_route")
    def long_string_route(self, long_long_string: longstr) -> InvocableResponse:
        return InvocableResponse(string=f"You gave me a long string {long_long_string}")
