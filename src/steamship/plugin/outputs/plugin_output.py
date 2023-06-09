from enum import Enum
from typing import List, Optional

from steamship.base.model import CamelModel


class OperationType(str, Enum):
    CREATE = "create"
    DELETE = "delete"
    RUN = "run"
    TRAIN = "train"
    EXISTS = "exists"
    EXISTS_TRAINED = "existsTrained"


class OperationUnit(str, Enum):
    CHARACTERS = "characters"
    UNITS = "units"
    BYTES = "bytes"
    MS = "ms"  # milliseconds
    TOKENS = "tokens"
    PROMPT_TOKENS = "promptTokens"
    SAMPLED_TOKENS = "sampledTokens"


class UsageReport(CamelModel):
    """This is the report object that a plugin or package can send back to notify the engine how much of something was consumed"""

    # What type of operation was performed
    operation_type: OperationType

    # What the unit of measurement is.
    operation_unit: OperationUnit

    # What the magnitude of measurement is
    operation_amount: int

    # A URL, if known, to an external audit object for this usage event
    audit_url: Optional[str]

    # An ID, if known, to an external record for this usage event
    audit_id: Optional[str]

    @staticmethod
    def run_tokens(tokens: int, audit_url: Optional[str] = None, audit_id: Optional[str] = None):
        return UsageReport(
            operation_type=OperationType.RUN,
            operation_unit=OperationUnit.TOKENS,
            operation_amount=tokens,
            audit_url=audit_url,
            audit_id=audit_id,
        )

    @staticmethod
    def run_units(units: int, audit_url: Optional[str] = None, audit_id: Optional[str] = None):
        return UsageReport(
            operation_type=OperationType.RUN,
            operation_unit=OperationUnit.UNITS,
            operation_amount=units,
            audit_url=audit_url,
            audit_id=audit_id,
        )

    @staticmethod
    def run_characters(
        characters: int, audit_url: Optional[str] = None, audit_id: Optional[str] = None
    ):
        return UsageReport(
            operation_type=OperationType.RUN,
            operation_unit=OperationUnit.CHARACTERS,
            operation_amount=characters,
            audit_url=audit_url,
            audit_id=audit_id,
        )


class PluginOutput(CamelModel):
    """Base class for all types of plugin output, allowing usage reporting"""

    usage: Optional[List[UsageReport]]
