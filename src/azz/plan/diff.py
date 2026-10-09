from collections.abc import Mapping, Sequence

from azz.backend import WorkItemBackend
from azz.core.work_item import WorkItem

from .comparison import field_diffs
from .models import Change, Changeset, ChangeType, FieldDiff, LocalItem
from .resolver import RemoteResolver
from .snapshot_diff import remote_advanced
from .snapshots import Snapshots


def compute_changeset(
    local_items: Sequence[LocalItem],
    engine: WorkItemBackend,
    snapshots: Snapshots,
) -> Changeset:
    """
    Compare every intent file against the remote.

    The remote lookups are batched, so the cost is one query rather than one
    subprocess per tracked file. The merge base decides which side moved: only
    the fields the file changed since its base are pushed, so a field edited on
    the remote alone is never reverted. Without a base, nothing is pushed.
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
    snapshots: Snapshots,
) -> Change:
    if local_item.item_id is None:
        return Change(local_item, ChangeType.CREATE)

    remote_item = remote_items.get(local_item.item_id)
    if remote_item is None:
        return Change(local_item, ChangeType.GONE)

    diffs = field_diffs(local_item, remote_item)
    base = snapshots.base.read_item(remote_item.id)
    if base is None:
        change_type = ChangeType.NO_BASE if diffs else ChangeType.NOOP
        return Change(local_item, change_type, diffs, remote_item)
    return _against_base(local_item, remote_item, base, diffs)


def _against_base(
    local_item: LocalItem,
    remote_item: WorkItem,
    base: WorkItem,
    diffs: Sequence[FieldDiff],
) -> Change:
    """Split the differences with the remote into the file's own edits, which
    are pushed, and the remote's, which only `azz plan pull` may bring in."""
    edited = {diff.field_name for diff in field_diffs(local_item, base)}
    own_edits = tuple(diff for diff in diffs if diff.field_name in edited)
    if own_edits:
        change_type = ChangeType.UPDATE
    else:
        change_type = ChangeType.BEHIND if diffs else ChangeType.NOOP
    return Change(
        local_item,
        change_type,
        own_edits or tuple(diffs),
        remote_item,
        remote_moved=remote_advanced(base, remote_item),
    )
