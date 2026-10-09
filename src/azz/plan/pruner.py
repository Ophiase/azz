from typing import Final

from .models import ApplyOutcome, Change, Changeset, ChangeType, PrunePolicy

CLOSED_ONLY: Final = PrunePolicy()


def prunable_changes(
    changeset: Changeset, policy: PrunePolicy = CLOSED_ONLY
) -> tuple[Change, ...]:
    """
    The intent files that hold nothing the remote does not already have.

    A file qualifies only when it is in agreement with a work item the policy
    calls inactive — Closed by default. Anything else — local drift, a remote
    that moved, a not-yet-created file, an item missing from the remote —
    carries information that deleting would lose.
    """
    return tuple(
        change
        for change in changeset.of_type(ChangeType.NOOP)
        if change.remote_item is not None
        and change.local_item.item_id is not None
        and policy.is_inactive(change.remote_item)
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
