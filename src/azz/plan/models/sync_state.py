from enum import StrEnum
from typing import Final


class SyncState(StrEnum):
    """
    How one intent file relates to the cache, decided three ways.

    The file is compared to the merge base (did the human move it?) and the
    merge base to the fetched snapshot (did the remote move?). No network, no
    heuristic.
    """

    IN_SYNC = "in_sync"
    LOCAL_ONLY = "local_only"
    REMOTE_ONLY = "remote_only"
    CONFLICT = "conflict"
    NEW = "new"
    UNKNOWN = "unknown"

    @property
    def label(self) -> str:
        return SYNC_STATE_LABELS[self]

    @property
    def style(self) -> str:
        return SYNC_STATE_COLORS[self]

    @property
    def description(self) -> str:
        return SYNC_STATE_DESCRIPTIONS[self]


SYNC_STATE_LABELS: Final = {
    SyncState.IN_SYNC: "SYNC",
    SyncState.LOCAL_ONLY: "LOCAL",
    SyncState.REMOTE_ONLY: "REMOTE",
    SyncState.CONFLICT: "CONFLICT",
    SyncState.NEW: "NEW",
    SyncState.UNKNOWN: "UNKNOWN",
}

SYNC_STATE_COLORS: Final = {
    SyncState.IN_SYNC: "grey50",
    SyncState.LOCAL_ONLY: "yellow",
    SyncState.REMOTE_ONLY: "cyan",
    SyncState.CONFLICT: "red",
    SyncState.NEW: "green",
    SyncState.UNKNOWN: "magenta",
}

SYNC_STATE_DESCRIPTIONS: Final = {
    SyncState.IN_SYNC: "✓ in sync",
    SyncState.LOCAL_ONLY: "→ local changes, safe to push",
    SyncState.REMOTE_ONLY: "→ remote moved, run azz plan pull",
    SyncState.CONFLICT: "→ both sides changed — resolve by hand",
    SyncState.NEW: "→ will be created by azz plan push",
    SyncState.UNKNOWN: "→ not in the cache, run azz plan fetch",
}
