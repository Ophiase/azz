from collections.abc import Sequence
from enum import StrEnum
from pathlib import Path
from typing import Final

from azz.cache import CacheStore
from azz.core.work_item import WorkItem

from .comparison import field_diffs
from .discovery import cache_directory, intent_file_paths
from .errors import IntentFileError
from .models import LocalItem
from .parser import parse_intent_files


class TrackingStatus(StrEnum):
    """How a remote work item relates to the local plan."""

    UNTRACKED = "untracked"
    IN_SYNC = "in_sync"
    LOCAL_AHEAD = "local_ahead"
    REMOTE_AHEAD = "remote_ahead"
    CONFLICT = "conflict"

    @property
    def glyph(self) -> str:
        return TRACKING_GLYPHS[self]

    @property
    def style(self) -> str:
        return TRACKING_COLORS[self]

    @property
    def description(self) -> str:
        return TRACKING_DESCRIPTIONS[self]


TRACKING_GLYPHS: Final = {
    TrackingStatus.UNTRACKED: " ",
    TrackingStatus.IN_SYNC: "●",
    TrackingStatus.LOCAL_AHEAD: "◆",
    TrackingStatus.REMOTE_AHEAD: "▼",
    TrackingStatus.CONFLICT: "✗",
}

TRACKING_COLORS: Final = {
    TrackingStatus.UNTRACKED: "grey50",
    TrackingStatus.IN_SYNC: "green",
    TrackingStatus.LOCAL_AHEAD: "yellow",
    TrackingStatus.REMOTE_AHEAD: "cyan",
    TrackingStatus.CONFLICT: "red",
}

TRACKING_DESCRIPTIONS: Final = {
    TrackingStatus.UNTRACKED: "not in .azz/tasks",
    TrackingStatus.IN_SYNC: "in sync with the remote",
    TrackingStatus.LOCAL_AHEAD: "local changes not pushed",
    TrackingStatus.REMOTE_AHEAD: "remote moved since the last fetch",
    TrackingStatus.CONFLICT: "local and remote both changed",
}


def tracking_statuses(
    plan_root: Path | None,
    remote_items: Sequence[WorkItem],
) -> dict[int, TrackingStatus]:
    """
    Classify each remote item against the local plan.

    Pure local I/O — one directory scan, no network. Safe to call on every
    TUI refresh. A `plan_root` of None (no `.azz` anywhere) yields an empty
    mapping, so callers can treat "no plan" as "everything untracked".

    Unparseable intent files are skipped rather than raised: a broken file
    must not take the TUI down.
    """
    if plan_root is None:
        return {}
    local_by_id = _local_items_by_id(plan_root)
    if not local_by_id:
        return {}
    store = CacheStore(cache_directory(plan_root))
    return {
        item.id: _classify(local_by_id[item.id], item, store)
        for item in remote_items
        if item.id in local_by_id
    }


def _local_items_by_id(plan_root: Path) -> dict[int, LocalItem]:
    try:
        local_items = parse_intent_files(intent_file_paths(plan_root))
    except IntentFileError:
        return {}
    return {item.item_id: item for item in local_items if item.item_id is not None}


def _classify(
    local_item: LocalItem, remote_item: WorkItem, store: CacheStore
) -> TrackingStatus:
    local_moved = bool(field_diffs(local_item, remote_item))
    cached = store.read_item(remote_item.id)
    if cached is None:
        return TrackingStatus.LOCAL_AHEAD if local_moved else TrackingStatus.IN_SYNC

    local_moved = bool(field_diffs(local_item, cached))
    remote_moved = _remote_moved_since_cache(remote_item, cached)
    if local_moved and remote_moved:
        return TrackingStatus.CONFLICT
    if local_moved:
        return TrackingStatus.LOCAL_AHEAD
    if remote_moved:
        return TrackingStatus.REMOTE_AHEAD
    return TrackingStatus.IN_SYNC


def _remote_moved_since_cache(remote_item: WorkItem, cached: WorkItem) -> bool:
    if remote_item.changed_date is None or cached.changed_date is None:
        return False
    return remote_item.changed_date > cached.changed_date
