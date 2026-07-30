from enum import StrEnum
from typing import Final


class FetchStatus(StrEnum):
    """What a fetch did to one entry of the cache."""

    CREATED = "created"
    REFRESHED = "refreshed"
    UNCHANGED = "unchanged"

    @property
    def label(self) -> str:
        return FETCH_STATUS_LABELS[self]

    @property
    def style(self) -> str:
        return FETCH_STATUS_COLORS[self]


FETCH_STATUS_LABELS: Final = {
    FetchStatus.CREATED: "NEW",
    FetchStatus.REFRESHED: "MOVED",
    FetchStatus.UNCHANGED: "SAME",
}

FETCH_STATUS_COLORS: Final = {
    FetchStatus.CREATED: "green",
    FetchStatus.REFRESHED: "cyan",
    FetchStatus.UNCHANGED: "grey50",
}
