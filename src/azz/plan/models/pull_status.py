from enum import StrEnum
from typing import Final


class PullStatus(StrEnum):
    CREATED = "created"
    FAST_FORWARDED = "fast_forwarded"
    UP_TO_DATE = "up_to_date"
    REFUSED = "refused"
    SKIPPED = "skipped"

    @property
    def label(self) -> str:
        return PULL_STATUS_LABELS[self]

    @property
    def style(self) -> str:
        return PULL_STATUS_COLORS[self]

    @property
    def is_quiet(self) -> bool:
        """Nothing happened, so a full archive does not print thousands of
        lines saying so."""
        return self is PullStatus.UP_TO_DATE


PULL_STATUS_LABELS: Final = {
    PullStatus.CREATED: "NEW",
    PullStatus.FAST_FORWARDED: "PULLED",
    PullStatus.UP_TO_DATE: "OK",
    PullStatus.REFUSED: "CONFLICT",
    PullStatus.SKIPPED: "KEPT",
}

PULL_STATUS_COLORS: Final = {
    PullStatus.CREATED: "green",
    PullStatus.FAST_FORWARDED: "cyan",
    PullStatus.UP_TO_DATE: "grey50",
    PullStatus.REFUSED: "red",
    PullStatus.SKIPPED: "yellow",
}
