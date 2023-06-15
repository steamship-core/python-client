from enum import Enum
from typing import List, Mapping, Optional

from pydantic.main import BaseModel


class JSONType(str, Enum):
    string = "string"
    number = "number"
    integer = "integer"
    object = "object"
    array = "array"
    boolean = "boolean"
    null = "null"


class FunctionProperty(BaseModel):
    """Schema for an individual parameter used in an OpenAI function."""

    type: JSONType = JSONType.object
    """Type of the property. Defaults to object."""

    description: str
    """Description of the property. Should include format instructions."""


class FunctionParameters(BaseModel):
    """Schema for the description of how to invoke an OpenAI function."""

    type: JSONType = JSONType.object
    """Type of this object. DO NOT MODIFY."""

    properties: Mapping[str, FunctionProperty]
    """Map of param names to their types and description"""

    required: Optional[List[str]] = []
    """List of required parameter names."""


class OpenAIFunction(BaseModel):
    """Schema for an OpenAI function that can be used in prompting."""

    name: str
    """Name of the function.  This will appear in LLM response."""

    description: str
    """Purpose of function. Should describe expected output (and format)."""

    parameters: FunctionParameters
    """Specifies how the function should be called."""
