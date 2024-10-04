from enum import Enum


class PanelType(Enum):
    LONGI505 = ("LONGi 505W", 2094, 1134)

    def __init__(self, *values) -> None:
        self.values = values

    def __str__(self) -> str:
        return self.values[0]

    @property
    def height_inches(self) -> float:
        return round(self.values[1] / 25.4, 4)

    @property
    def width_inches(self) -> float:
        return round(self.values[2] / 25.4, 4)

    @classmethod
    def map(cls):
        return {str(e): e for e in cls}


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
