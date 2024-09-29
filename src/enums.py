from enum import Enum


class PanelType(Enum):
    LONGI505 = ("LONGi 505W", 2094, 1134)

    def __init__(self, *values) -> None:
        self.values = values

    @property
    def name(self) -> str:
        return self.values[0]

    @property
    def height_inches(self) -> float:
        return round(self.values[1] / 25.4, 4)

    @property
    def width_inches(self) -> float:
        return round(self.values[2] / 25.4, 4)

    @classmethod
    def map(cls):
        return {panel.name: panel for panel in cls}
