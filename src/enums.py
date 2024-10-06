from enum import Enum


class RackingPattern(Enum):
    CONTINUOUS = "Continuous"
    STAGGERED = "Staggered"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def map(cls):
        return {str(e): e for e in cls}


class RafterSpacing(Enum):
    TWELVE = "12"
    SIXTEEN = "16"
    NINETEEN_AND_THREE_SIXTEENTHS = "19.1875"
    TWENTY_FOUR = "24"
    THIRTY_TWO = "32"
    FORTY_EIGHT = "48"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def map(cls):
        return {str(e): e for e in cls}
