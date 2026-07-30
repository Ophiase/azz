from enum import StrEnum
from typing import Final


class FetchStatus(StrEnum):
    CREATED = "created"
    REFRESHED = "refreshed"
    SKIPPED = "skipped"

    @property
    def label(self) -> str:
        return FETCH_STATUS_LABELS[self]

    @property
    def style(self) -> str:
        return FETCH_STATUS_COLORS[self]


FETCH_STATUS_LABELS: Final = {
    FetchStatus.CREATED: "NEW",
    FetchStatus.REFRESHED: "SYNCED",
    FetchStatus.SKIPPED: "KEPT",
}

FETCH_STATUS_COLORS: Final = {
    FetchStatus.CREATED: "green",
    FetchStatus.REFRESHED: "cyan",
    FetchStatus.SKIPPED: "yellow",
}
