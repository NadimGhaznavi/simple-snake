from dataclasses import dataclass


# dataclass generates initialization and equality; frozen prevents field reassignment.
# Here it also generates a hash, allowing Points in sets of occupied cells.
# https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass
@dataclass(frozen=True)
class Point:
    x: int
    y: int
