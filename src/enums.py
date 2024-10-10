from enum import Enum


class MappedStringEnum(Enum):
    def __str__(self) -> str:
        return self.value

    @classmethod
    def map(cls):
        return {e.value: e for e in cls}


class RackingPattern(MappedStringEnum):
    CONTINUOUS = "Continuous"
    STAGGERED = "Staggered"


class RafterSpacing(MappedStringEnum):
    TWELVE = "12"
    SIXTEEN = "16"
    NINETEEN_AND_THREE_SIXTEENTHS = "19.1875"
    TWENTY_FOUR = "24"
    THIRTY_TWO = "32"
    FORTY_EIGHT = "48"
