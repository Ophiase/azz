from dataclasses import dataclass

from .change import Change


@dataclass(frozen=True, slots=True)
class ApplyOutcome:
    change: Change
    message: str
    succeeded: bool
