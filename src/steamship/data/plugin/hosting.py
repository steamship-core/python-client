from enum import Enum


class HostingType(str, Enum):
    """The type of hosting provider to deploy to."""

    LAMBDA = "lambda"
    ECS = "ecs"


class HostingEnvironment(str, Enum):
    """The software environment required for deployment."""

    PYTHON38 = "python38"
    STEAMSHIP_PYTORCH_CPU = "inferenceCpu"


class HostingMemory(str, Enum):
    """The amount of memory required for deployment.

    This is mapped to a value dependent on the HostingType it is combined with.
    """

    MIN = "min"
    XXS = "xxs"
    XS = "xs"
    SM = "sm"
    MD = "md"
    LG = "lg"
    XL = "xl"
    XXL = "xxl"
    MAX = "max"


class HostingCpu(str, Enum):
    """The amount of CPU required for deployment.

    This is mapped to a value dependent on the HostingType it is combined with.
    """

    MIN = "min"
    XXS = "xxs"
    XS = "xs"
    SM = "sm"
    MD = "md"
    LG = "lg"
    XL = "xl"
    XXL = "xxl"
    MAX = "max"


class HostingTimeout(str, Enum):
    """The request timeout required for deployment.

    This is mapped to a value dependent on the HostingType it is combined with.
    """

    MIN = "min"
    XXS = "xxs"
    XS = "xs"
    SM = "sm"
    MD = "md"
    LG = "lg"
    XL = "xl"
    XXL = "xxl"
    MAX = "max"
