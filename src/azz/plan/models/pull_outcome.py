from dataclasses import dataclass
from pathlib import Path

from .pull_status import PullStatus


@dataclass(frozen=True, slots=True)
class PullOutcome:
    path: Path
    item_id: int | None
    status: PullStatus
    reason: str = ""
