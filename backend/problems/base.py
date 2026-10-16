from dataclasses import dataclass
from random import Random

@dataclass
class Param:
    name: str
    label: str
    default: int

@dataclass
class Problem:
    question: str        # will be latex
    answer: str          # will be latex

class ProblemType:
    id: str = ""
    topic: str = ""
    label: str = ""
    params: list[Param] = []

    def validate(self, params: dict) -> dict:
        cleaned = {p.name: p.default for p in self.params}

        for key, value in params.items():
            if key not in cleaned:
                raise ValueError(f"Unknown parameter: {key}")
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{key} must be a whole number")
            cleaned[key] = value

        self.check(cleaned)
        return cleaned

    def check(self, params: dict) -> None:
        """Rules specific to one problem type. Subclasses override this."""

    def generate(self, params: dict, rng: Random) -> Problem:
        raise NotImplementedError