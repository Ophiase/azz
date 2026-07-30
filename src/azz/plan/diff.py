from collections.abc import Mapping, Sequence

from azz.core.engine import Engine
from azz.core.work_item import WorkItem

from .comparison import field_diffs
from .freshness import remote_is_ahead
from .models import Change, Changeset, ChangeType, LocalItem
from .resolver import RemoteResolver


def compute_changeset(
    local_items: Sequence[LocalItem],
    engine: Engine,
) -> Changeset:
    """
    Compare every intent file against the remote.

    The remote lookups are batched, so the cost is one query rather than one
    subprocess per tracked file.
    """
    remote_items = RemoteResolver(engine).resolve(_tracked_ids(local_items))
    return Changeset(
        tuple(_compute_change(item, remote_items) for item in local_items)
    )


def _tracked_ids(local_items: Sequence[LocalItem]) -> tuple[int, ...]:
    return tuple(
        item.item_id for item in local_items if item.item_id is not None
    )


def _compute_change(
    local_item: LocalItem, remote_items: Mapping[int, WorkItem]
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
        remote_moved=remote_is_ahead(local_item, remote_item),
    )
