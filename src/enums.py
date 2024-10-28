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
