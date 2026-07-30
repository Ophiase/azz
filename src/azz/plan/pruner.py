from azz.core.work_item import WorkItemState

from .models import ApplyOutcome, Change, Changeset, ChangeType


def prunable_changes(changeset: Changeset) -> tuple[Change, ...]:
    """
    The intent files that hold nothing the remote does not already have.

    A file qualifies only when it is byte-for-byte in agreement with a Closed
    work item. Anything else — local drift, a not-yet-created file, an item
    missing from the remote — carries information that deleting would lose.
    """
    return tuple(
        change
        for change in changeset.of_type(ChangeType.NOOP)
        if _is_closed(change) and change.local_item.item_id is not None
    )


def prune_intent_file(change: Change) -> ApplyOutcome:
    """Delete the local file. The remote work item is never touched."""
    path = change.local_item.path
    try:
        path.unlink()
    except OSError as error:
        return ApplyOutcome(
            change, f"could not delete {path.name}: {error}", succeeded=False
        )
    return ApplyOutcome(change, f"deleted {path.name}", succeeded=True)


def _is_closed(change: Change) -> bool:
    remote_item = change.remote_item
    return remote_item is not None and remote_item.state == WorkItemState.CLOSED
