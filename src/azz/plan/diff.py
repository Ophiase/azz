from collections.abc import Sequence
from logging import getLogger

from azz.core.engine import Engine
from azz.core.work_item import WorkItem

from .comparison import field_diffs
from .freshness import remote_is_ahead
from .models import Change, Changeset, ChangeType, LocalItem

logger = getLogger(__name__)


def compute_changeset(
    local_items: Sequence[LocalItem],
    engine: Engine,
) -> Changeset:
    return Changeset(tuple(_compute_change(item, engine) for item in local_items))


def _compute_change(local_item: LocalItem, engine: Engine) -> Change:
    if local_item.item_id is None:
        return Change(local_item, ChangeType.CREATE)

    remote_item = _fetch_remote(local_item.item_id, engine)
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


def _fetch_remote(work_item_id: int, engine: Engine) -> WorkItem | None:
    try:
        return engine.get_workitem(work_item_id)
    except RuntimeError:
        logger.debug("work item %s not reachable on the remote", work_item_id)
        return None
