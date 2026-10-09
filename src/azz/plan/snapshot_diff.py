from azz.core.work_item import WorkItem

from .comparison import iteration_name, normalize_markdown


def remote_advanced(base: WorkItem, later: WorkItem) -> bool:
    """
    Whether the remote moved between two snapshots of the same work item.

    Content, not timestamps: Azure DevOps bumps `System.ChangedDate` for fields
    the plan does not track, and reporting those as a remote change would send
    the user to `azz plan pull` for a rewrite that changes nothing.
    """
    return _signature(base) != _signature(later) or _priority_moved(base, later)


def _signature(work_item: WorkItem) -> tuple[str, ...]:
    """Exactly the fields an intent file can express. The body is compared as
    stored, not as read: the two snapshots may come from `az` commands that
    declare its format differently, and the same text must not read as a move."""
    return (
        work_item.name,
        str(work_item.state),
        str(work_item.item_type),
        str(work_item.parent_id or ""),
        iteration_name(work_item) or "",
        normalize_markdown(work_item.description),
    )


def _priority_moved(base: WorkItem, later: WorkItem) -> bool:
    """A base cached before priorities were fetched has none; that is not a
    remote move, or every edited file would turn into a conflict."""
    return base.priority is not None and base.priority != later.priority
