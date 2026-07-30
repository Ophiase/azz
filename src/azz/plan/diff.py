from collections.abc import Mapping, Sequence

from azz.core.engine import Engine
from azz.core.work_item import WorkItem

from .comparison import field_diffs
from .models import Change, Changeset, ChangeType, LocalItem
from .resolver import RemoteResolver
from .snapshot_diff import remote_advanced
from .snapshots import Snapshots


def compute_changeset(
    local_items: Sequence[LocalItem],
    engine: Engine,
    snapshots: Snapshots | None = None,
) -> Changeset:
    """
    Compare every intent file against the remote.

    The remote lookups are batched, so the cost is one query rather than one
    subprocess per tracked file. Given the cache, the merge base also says
    whether the remote moved since the last sync — without it that question
    goes unanswered rather than guessed.
    """
    remote_items = RemoteResolver(engine).resolve(_tracked_ids(local_items))
    return Changeset(
        tuple(_compute_change(item, remote_items, snapshots) for item in local_items)
    )


def _tracked_ids(local_items: Sequence[LocalItem]) -> tuple[int, ...]:
    return tuple(item.item_id for item in local_items if item.item_id is not None)


def _compute_change(
    local_item: LocalItem,
    remote_items: Mapping[int, WorkItem],
    snapshots: Snapshots | None,
) -> Change:
    if local_item.item_id is None:
        return Change(local_item, ChangeType.CREATE)

    remote_item = remote_items.get(local_item.item_id)
    if remote_item is None:
        return Change(local_item, ChangeType.GONE)

    diffs = field_diffs(local_item, remote_item)
    change_type = ChangeType.UPDATE if diffs else ChangeType.NOOP
    return Change(
        local_item,
        change_type,
        diffs,
        remote_item,
        remote_moved=_remote_moved(remote_item, snapshots),
    )


def _remote_moved(remote_item: WorkItem, snapshots: Snapshots | None) -> bool:
    if snapshots is None:
        return False
    base = snapshots.base.read_item(remote_item.id)
    return base is not None and remote_advanced(base, remote_item)
